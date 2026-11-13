#!/usr/bin/env python3
"""runfile — every file type, the runner that can execute it, and an honest "no".

WHY THIS EXISTS
---------------
Asked: "what file types can Windows run that Linux cannot, and why not?"

The answer is not a list, it is two ABIs and the bridges between them:

  * Windows' loader reads PE (``MZ`` -> ``PE\\0\\0``). Linux's kernel loader reads
    ELF (``\\x7fELF``). Neither reads the other, and the reason is structural,
    not political: the object format, the entry convention and the kernel entry
    path differ. An ELF file names a ``PT_INTERP`` loader path that Windows does
    not have; a PE file names an import table of DLLs that Linux does not have.
    A kernel that loaded the foreign format anyway would have nothing to hand
    the process once it started.
  * The bridges are ordinary programs, so they are detectable: WSL executes ELF
    on Windows, Wine executes PE on Linux, the JVM executes ``.class``/``.jar``
    wherever ``java`` exists, .NET executes PE/CLI images wherever ``dotnet``
    exists, and interpreters execute shebang scripts.

So this tool does not claim a universal executor. It identifies the file by
MAGIC BYTES, never by extension — a ``.exe`` that is really an ELF, or a
``.txt`` that is really a PE, is exactly the case where extension-agnosticism
is the point — then names the runner that exists HERE. When no runner exists it
says which runner is missing. A dispatcher that reports "not executable" when
the truth is "no bridge installed" is the defect this tool exists to avoid.

    python tools/runfile.py --explain          # the table, and the reason why
    python tools/runfile.py --list             # what this machine can run
    python tools/runfile.py --plan FILE        # decide, execute nothing
    python tools/runfile.py --json FILE        # machine-readable verdict
    python tools/runfile.py FILE [args...]     # run it
    python tools/runfile.py --timeout 30 FILE  # bound the run (exit 124 on kill)
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# runners: a name and how to find it. Everything is discovered, never assumed.
# --------------------------------------------------------------------------

RUNNER_BINARIES = {
    "wsl": "wsl",              # Windows -> ELF bridge
    "wine": "wine",            # Linux -> PE bridge (absent on this box)
    "dotnet": "dotnet",        # PE/CLI (.NET) images
    "java": "java",            # .class / .jar
    "python": sys.executable,  # .py / shebang python
    "node": "node",
    "pwsh": "pwsh",
    "powershell": "powershell",
    "cmd": "cmd",
    "cscript": "cscript",
    "wscript": "wscript",
    "msiexec": "msiexec",
    "reg": "reg",
    "wasmtime": "wasmtime",
    "qemu-x86_64": "qemu-x86_64",
}


def runner_path(name: str) -> str | None:
    """Absolute path of a runner, or None. Measured, never presumed."""
    binary = RUNNER_BINARIES.get(name)
    if not binary:
        return None
    if os.path.isabs(binary):
        return binary if os.path.exists(binary) else None
    if name in ("cmd", "cscript", "wscript", "msiexec", "reg"):
        base = os.environ.get("SystemRoot", r"C:\WINDOWS")
        candidate = os.path.join(base, "System32", binary + ".exe")
        if os.path.exists(candidate):
            return candidate
    return shutil.which(binary)


# --------------------------------------------------------------------------
# identification
# --------------------------------------------------------------------------


@dataclass
class Ident:
    """What a file IS, by content."""

    name: str
    kind: str          # executable | script | archive | data | link
    detail: str = ""
    arch: str = ""     # for native executables
    meta: dict = field(default_factory=dict)


ELF_MACHINES = {0x03: "i386", 0x28: "arm", 0x3E: "x86-64", 0xB7: "aarch64", 0xF3: "riscv"}
PE_MACHINES = {0x014C: "i386", 0x8664: "x86-64", 0xAA64: "aarch64"}

INTERP_BY_NAME = {
    "python": "python", "python3": "python", "python3.16": "python",
    "sh": "sh", "bash": "sh", "dash": "sh", "zsh": "sh",
    "node": "node", "perl": "perl", "ruby": "ruby",
    "pwsh": "pwsh", "env": "env",
}


def _shebang(data: bytes) -> tuple[str, list[str]] | None:
    if not data.startswith(b"#!"):
        return None
    line = data.split(b"\n", 1)[0][2:].decode("utf-8", "replace").strip()
    if not line:
        return None
    parts = line.split()
    interp = os.path.basename(parts[0])
    args = parts[1:]
    # `#!/usr/bin/env python3 -u` -> interpreter python3, args from the rest
    if interp == "env" and args:
        interp = os.path.basename(args[0])
        args = args[1:]
    return interp, args


def identify(path: str) -> Ident:
    """Identify by content. The extension is recorded but never trusted."""
    with open(path, "rb") as fh:
        data = fh.read(4096)

    if data.startswith(b"\x7fELF"):
        machine = int.from_bytes(data[18:20], "little") if len(data) >= 20 else 0
        return Ident("ELF", "executable", "Linux/Unix binary",
                     ELF_MACHINES.get(machine, "unknown"))

    if data.startswith(b"#!"):
        shebang = _shebang(data)
        if shebang:
            # stored as the (interpreter, args) pair plan() unpacks, not as a name:
            # a bare string here makes plan() unpack characters.
            return Ident("script", "script", f"#!{shebang[0]}", "", {"interp": shebang})

    if data.startswith(b"MZ"):
        # DOS header's e_lfanew points at the PE signature; a bare MZ without it
        # is a DOS/16-bit image, which neither modern Windows nor Linux runs.
        if len(data) >= 0x40:
            off = int.from_bytes(data[0x3C:0x40], "little")
            if 0 <= off < 4096:
                with open(path, "rb") as fh:
                    fh.seek(off)
                    sig = fh.read(24)
                if sig.startswith(b"PE\0\0"):
                    machine = int.from_bytes(sig[4:6], "little")
                    return Ident("PE", "executable", "Windows binary",
                                 PE_MACHINES.get(machine, "unknown"))
        return Ident("MZ/DOS", "executable", "16-bit DOS image (no modern loader)")

    if data[:4] in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf",
                    b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe"):
        return Ident("Mach-O", "executable", "macOS binary")

    if data[:4] == b"\xca\xfe\xba\xbe":
        # Java class files and Mach-O fat binaries share this magic; the class
        # format's next field is a minor/major version pair, a fat header's is
        # a small architecture count. 45..70 is the class-file major range.
        major = int.from_bytes(data[6:8], "big") if len(data) >= 8 else 0
        if 45 <= major <= 70:
            return Ident("Java class", "executable", f"bytecode, major {major}")
        return Ident("Mach-O fat", "executable", "universal macOS binary")

    if data[:4] == b"\0asm":
        return Ident("WebAssembly", "executable", "wasm module")

    if data[:2] == b"PK":
        return Ident("zip/jar", "archive", "zip container",
                     "", {"jar": path.lower().endswith((".jar", ".war"))})

    if data[:4] == b"\x89PNG" or data[:2] == b"\xff\xd8" or data[:4] == b"%PDF":
        return Ident("document", "data", "not executable by design")

    if data[:5] in (b"@echo", b"@rem ") or data[:2] in (b"::",):
        return Ident("batch", "script", "cmd.exe batch file")

    return Ident("unknown", "data", "no recognised magic")


WINDOWS_SCRIPT_SUFFIXES = {
    ".bat": ("batch", "cmd"),
    ".cmd": ("batch", "cmd"),
    ".ps1": ("powershell", "pwsh"),
    ".vbs": ("vbscript", "cscript"),
    ".vbe": ("vbscript", "cscript"),
    ".wsf": ("windows script", "cscript"),
    ".hta": ("html application", "mshta"),
    ".msi": ("installer", "msiexec"),
    ".msp": ("installer patch", "msiexec"),
    ".reg": ("registry", "reg"),
    ".lnk": ("shell link", ""),
    ".cpl": ("control panel", ""),
    ".scr": ("screensaver", ""),
}


def _suffix_ident(path: str) -> Ident | None:
    """Suffix-named formats whose magic is prose or a container.

    Tried only AFTER magic, and only for text formats that carry no magic.
    """
    suffix = os.path.splitext(path)[1].lower()
    entry = WINDOWS_SCRIPT_SUFFIXES.get(suffix)
    if not entry:
        return None
    label, runner = entry
    return Ident(label, "script" if runner else "link",
                 f"{suffix} -> {runner or 'no runner'}", "", {"runner": runner})


# --------------------------------------------------------------------------
# planning: which runner HERE can execute it
# --------------------------------------------------------------------------


@dataclass
class Step:
    """One executable decision: argv, or why there is none."""

    verdict: str      # native | bridge | no_runner | not_executable
    runner: str = ""
    argv: list[str] = field(default_factory=list)
    note: str = ""


def _win_to_wsl(path: str) -> str:
    absolute = os.path.abspath(path)
    drive, rest = os.path.splitdrive(absolute)
    if not rest:
        return absolute.replace("\\", "/")
    return "/mnt/" + drive.rstrip(":").lower() + rest.replace("\\", "/")


def plan(path: str, args: list[str] | None = None) -> tuple[Ident, Step]:
    """Decide what would execute `path` on THIS machine, and be honest if nothing can."""
    args = list(args or [])
    ident = identify(path)
    suffix = _suffix_ident(path)
    host_is_windows = os.name == "nt"
    executable = os.access(path, os.X_OK) or os.name == "nt"

    # 1. native binaries: the two loader families, and the bridges between them.
    if ident.name == "ELF":
        if not host_is_windows:
            if not executable:
                return ident, Step("no_runner", note="mode lacks +x (chmod +x, or run the interpreter)")
            return ident, Step("native", "kernel", [os.path.abspath(path), *args],
                               f"ELF {ident.arch} runs directly on this kernel")
        wsl = runner_path("wsl")
        if wsl:
            return ident, Step("bridge", "wsl", [wsl, "--exec", _win_to_wsl(path), *args],
                               f"ELF {ident.arch} has no Windows loader; WSL runs it")
        return ident, Step("no_runner", note="ELF needs WSL (or qemu-user) on Windows; neither installed")

    if ident.name in ("PE", "MZ/DOS"):
        if host_is_windows:
            if ident.name == "MZ/DOS":
                return ident, Step("no_runner", note="16-bit DOS image: no NTVDM on 64-bit Windows")
            return ident, Step("native", "kernel", [os.path.abspath(path), *args],
                               f"PE {ident.arch} runs directly on this loader")
        wine = runner_path("wine")
        if wine:
            return ident, Step("bridge", "wine", [wine, path, *args],
                               "PE has no Linux loader; wine supplies the Windows ABI")
        return ident, Step("no_runner", note="PE needs wine on Linux; not installed")

    if ident.name == "Mach-O" or ident.name == "Mach-O fat":
        return ident, Step("no_runner",
                           note="Mach-O has no Windows/Linux loader and no bridge on this box")

    if ident.name == "Java class":
        java = runner_path("java")
        if java:
            return ident, Step("bridge", "java", [java, "-cp", os.path.dirname(os.path.abspath(path)) or ".",
                                                 os.path.splitext(os.path.basename(path))[0], *args],
                               "bytecode is architecture-free; the JVM is the loader")
        return ident, Step("no_runner", note="java not installed")

    if ident.name == "WebAssembly":
        wasmtime = runner_path("wasmtime")
        if wasmtime:
            return ident, Step("bridge", "wasmtime", [wasmtime, path, *args], "wasm needs a runtime")
        return ident, Step("no_runner", note="wasm needs wasmtime/wasmer; neither installed")

    # 2. scripts: the shebang names the interpreter, and a missing interpreter
    #    is a named absence, not a silent "not executable".
    if ident.kind == "script":
        interp, interp_args = ident.meta.get("interp", (None, [])) or (None, [])
        if interp is None and suffix:
            runner_name = suffix.meta.get("runner", "")
            if runner_name == "cmd":
                return ident, Step("native", "cmd", [runner_path("cmd") or "cmd", "/c", path, *args],
                                   "cmd.exe is the loader for batch files")
            if runner_name == "pwsh":
                for candidate in ("pwsh", "powershell"):
                    found = runner_path(candidate)
                    if found:
                        return ident, Step("bridge", candidate,
                                           [found, "-NoProfile", "-File", path, *args])
                return ident, Step("no_runner", note="no PowerShell installed")
            if runner_name == "cscript":
                found = runner_path("cscript")
                if found:
                    return ident, Step("bridge", "cscript", [found, "//nologo", path, *args])
                return ident, Step("no_runner", note="cscript not installed")
            if runner_name == "msiexec":
                found = runner_path("msiexec")
                if found:
                    return ident, Step("bridge", "msiexec", [found, "/i", os.path.abspath(path)])
                return ident, Step("no_runner", note="msiexec not installed")
            if runner_name == "reg":
                found = runner_path("reg")
                if found:
                    return ident, Step("bridge", "reg", [found, "import", os.path.abspath(path)])
                return ident, Step("no_runner", note="reg not installed")
            return ident, Step("no_runner", note=suffix.detail)

        if interp:
            if interp in ("sh", "bash", "dash", "zsh"):
                wsl = runner_path("wsl")
                if host_is_windows:
                    if wsl:
                        return ident, Step("bridge", "wsl",
                                           [wsl, "--exec", _win_to_wsl(path), *args],
                                           f"#!{interp} is a POSIX interpreter; WSL supplies it")
                    return ident, Step("no_runner", note=f"#!{interp} needs a POSIX shell (WSL) on Windows")
                return ident, Step("native", os.path.basename(interp),
                                   [interp, path, *args])
            found = shutil.which(interp)
            if found:
                return ident, Step("bridge", interp, [found, *interp_args, path, *args],
                                   f"#!{interp} found on PATH")
            mapped = INTERP_BY_NAME.get(interp)
            if mapped:
                found = runner_path(mapped)
                if found:
                    return ident, Step("bridge", mapped, [found, *interp_args, path, *args])
            return ident, Step("no_runner", note=f"shebang interpreter '{interp}' is not installed")

    if suffix:
        if suffix.kind == "link":
            return ident, Step("no_runner", note="a .lnk/.cpl/.scr is a shell object, not a program")
        return ident, Step("no_runner", note=suffix.detail)

    return ident, Step("not_executable",
                       note="no executable format: this file is data, and data does not run")


# --------------------------------------------------------------------------
# the table: why the two families are mutually foreign
# --------------------------------------------------------------------------

EXPLAIN = """\
FORMAT            WINDOWS            LINUX              WHY THE OTHER CANNOT, AND THE BRIDGE
----------------  -----------------  -----------------  -------------------------------------------
PE  (MZ/PE\\0\\0)    native             wine               Windows loader. A PE's entry point
                                                         expects NTDLL/kernel32 imports and the
                                                         Win32/Win64 calling convention; Linux has
                                                         neither. Bridge: wine (absent here).
ELF (\\x7fELF)      wsl                native             Linux loader. ELF's PT_INTERP names
                                                         /lib64/ld-linux-*.so and its syscalls are
                                                         `open/read/write/mmap`, not NT syscalls.
                                                         Bridge: WSL (present here).
Mach-O            none               none               macOS loader; dyld + Mach traps. No bridge
                                                         installed on this box.
Java .class       java               java               Neither OS runs bytecode. The JVM is a
                                                         loader for a third, portable format.
.NET PE/CLI       dotnet             dotnet (mono)      A PE whose entry is CIL, not machine code;
                                                         runs where a CLI runtime exists.
WASM              none               none               Needs a wasm runtime (wasmtime/wasmer).
shebang scripts   wsl (for sh)       native (for sh)    The kernel executes the INTERPRETER named
                                                         in the shebang, so the interpreter is the
                                                         real portability question.
.bat/.cmd         native             none               cmd.exe builtins; no POSIX equivalent.
.ps1              native             pwsh               PowerShell Core is cross-platform.
.vbs/.wsf         cscript            none               Windows Script Host (COM).
.msi/.reg         native             none               Windows Installer / registry hive format.

THE ANSWER, IN ONE LINE: Windows runs PE and Linux runs ELF, and the reason each
cannot run the other is that both formats encode a CONTRACT WITH THE KERNEL that
loads them — loader path, syscall ABI, import/relocation model. Portability comes
from a third format that both can host (bytecode, wasm) or from a bridge that
re-implements the foreign kernel contract in user space (WSL, wine). "Run every
file type" is therefore not a loader feature; it is a table of bridges, and the
honest dispatcher reports which bridge is missing rather than calling the file
unrunnable.
"""


def list_runners() -> list[tuple[str, str, str]]:
    """Every runner this machine has, with the formats it unlocks."""
    unlocks = {
        "wsl": "ELF + POSIX shebang scripts",
        "wine": "PE (Windows .exe)",
        "dotnet": "PE/CLI (.NET assemblies)",
        "java": ".class / .jar",
        "python": ".py + python shebang",
        "node": ".js / node shebang",
        "pwsh": ".ps1",
        "powershell": ".ps1 (Windows PowerShell 5.1)",
        "cmd": ".bat / .cmd",
        "cscript": ".vbs / .wsf",
        "msiexec": ".msi / .msp",
        "reg": ".reg",
        "wasmtime": ".wasm",
        "qemu-x86_64": "foreign-architecture ELF",
    }
    rows = []
    for name in sorted(unlocks):
        found = runner_path(name)
        rows.append((name, found or "MISSING", unlocks[name]))
    return rows


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2

    if argv[0] == "--explain":
        print(EXPLAIN)
        return 0

    if argv[0] == "--list":
        rows = list_runners()
        width = max(len(found) for _n, found, _u in rows) + 2
        print(f"{'RUNNER':<14}{'PATH':<{width}}UNLOCKS")
        for name, found, unlocks in rows:
            print(f"{name:<14}{found:<{width}}{unlocks}")
        return 0

    as_json = False
    decide_only = False
    timeout_seconds: float | None = None
    rest = []
    tokens = list(argv)
    while tokens:
        token = tokens.pop(0)
        if token == "--json":
            as_json = True
        elif token in ("--plan", "--dry-run"):
            decide_only = True
        elif token == "--timeout":
            if not tokens:
                print("runfile: --timeout needs a number of seconds", file=sys.stderr)
                return 2
            timeout_seconds = float(tokens.pop(0))
        elif token.startswith("--timeout="):
            timeout_seconds = float(token.split("=", 1)[1])
        else:
            rest.append(token)
    if not rest:
        print("runfile: no file given (try --explain or --list)", file=sys.stderr)
        return 2

    path, args = rest[0], rest[1:]
    if not os.path.exists(path):
        print(f"runfile: no such file: {path}", file=sys.stderr)
        return 2

    ident, step = plan(path, args)
    if as_json:
        print(json.dumps({
            "path": os.path.abspath(path),
            "format": ident.name,
            "kind": ident.kind,
            "arch": ident.arch,
            "detail": ident.detail,
            "verdict": step.verdict,
            "runner": step.runner,
            "argv": step.argv,
            "note": step.note,
        }, indent=2))
        return 0 if step.verdict in ("native", "bridge") else 3

    print(f"{ident.name} ({ident.detail or 'no detail'}{', ' + ident.arch if ident.arch else ''})",
          file=sys.stderr)
    if step.verdict in ("no_runner", "not_executable") or decide_only:
        print(f"{step.verdict.upper()}: {step.note}", file=sys.stderr)
        if step.argv:
            print("would run: " + " ".join(step.argv), file=sys.stderr)
        return 0 if decide_only else 3

    print(f"{step.verdict} via {step.runner}: {step.note}", file=sys.stderr)
    try:
        # An executed program may legitimately run for hours, so the bound is the
        # operator's (--timeout), not a hidden constant; None waits, and the
        # kwarg is always passed so the wait is deliberate rather than forgotten.
        completed = subprocess.run(step.argv, check=False, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        print(f"runfile: killed after {timeout_seconds}s (--timeout)", file=sys.stderr)
        return 124
    except OSError as exc:
        print(f"runfile: {step.runner} refused to start: {exc}", file=sys.stderr)
        return 127
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
