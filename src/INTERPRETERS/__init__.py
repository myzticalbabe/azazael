#!/usr/bin/env python3
"""
Azazael Interpreters Package
=============================
Unified dispatcher for multi-language code execution.
Built to mirror the openmono-rebuild pattern: each language gets a dedicated
runner class with compile, run, test, and lint capabilities.

Supported: Python, Rust (1.95+), Go (1.26+), Bash, JavaScript (Node).

Usage:
    from INTERPRETERS import run_code
import argparse
    result = run_code("rust", 'fn main() { println!("Hello"); }')

OpenMono Integration:
    The InterpreterRouter mirrors the openmono OpenMonoDispatcher pattern.
    Each language runner (RustRunner, GoRunner) follows the same lifecycle:
        parse -> compile -> run -> test -> lint -> report.
        See: openmono_1click_commands.html on Desktop for CLI reference.
"""

import os
# from typing import List  # removed — all names have native equivalents
from dataclasses import dataclass
from typing import List

#: Swallows recorded when the failure ledger is unavailable (it is a stdlib-only
#: leaf, so this fallback should never fire -- if it does, the ledger is missing).

try:
    from CORE.failure_ledger import note_failure
except ImportError:                               # never break the host
    def note_failure(where: str, exc: BaseException | None = None) -> None:
        pass  # ledger missing; evidence-vs-silence tradeoff capped here


@dataclass
class RunResult:
    """Unified result from any language runner."""
    language: str
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    duration_ms: float = 0.0
    binary_path: str = ""


def run_python(code: str, args: list[str] = None) -> RunResult:
    """Run Python code via exec."""
    import io
    import time
    from contextlib import redirect_stdout, redirect_stderr

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    start = time.time()

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, {"__name__": "__main__"})
        success = True
        returncode = 0
    except Exception as e:
        note_failure("__init__:L55", e)
        stderr_capture.write(f"{type(e).__name__}: {e}\n")
        success = False
        returncode = 1

    return RunResult(
        language="python",
        success=success,
        stdout=stdout_capture.getvalue(),
        stderr=stderr_capture.getvalue(),
        returncode=returncode,
        duration_ms=(time.time() - start) * 1000,
    )


def run_rust(code: str, args: list[str] = None) -> RunResult:
    """Run Rust code via rust_runner."""
    from INTERPRETERS.rust_runner import RustRunner

    runner = RustRunner()
    result = runner.run_code(code, args)
    return RunResult(
        language="rust",
        success=result.success,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
        duration_ms=result.duration_ms,
        binary_path=result.binary_path or "",
    )


def run_go(code: str, args: list[str] = None) -> RunResult:
    """Run Go code via go_runner."""
    from INTERPRETERS.go_runner import GoRunner

    runner = GoRunner()
    result = runner.run_code(code, args)
    return RunResult(
        language="go",
        success=result.success,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=result.returncode,
        duration_ms=result.duration_ms,
        binary_path=result.binary_path or "",
    )


def run_bash(command: str) -> RunResult:
    """Run a bash command.

    NOTE: shell=True is INTENTIONAL here — this is a bash command runner.
    The `command` parameter is user-supplied and is meant to be arbitrary shell.
    This function is the designated shell execution path for the interpreter.
    Do NOT pass untrusted input through this function without sanitization.
    """
    import subprocess
    import time

    start = time.time()
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        return RunResult(
            language="bash",
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        note_failure("__init__:L128", e)
        return RunResult(
            language="bash",
            success=False,
            stderr=str(e),
            returncode=1,
        )


def run_javascript(code: str) -> RunResult:
    """Run JavaScript code via Node.js."""
    import subprocess
    import tempfile
    import time

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False
    ) as f:
        f.write(code)
        temp_path = f.name

    start = time.time()
    try:
        result = subprocess.run(
            ["node", temp_path], capture_output=True, text=True, timeout=30
        )
        return RunResult(
            language="javascript",
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            duration_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        note_failure("__init__:L162", e)
        return RunResult(
            language="javascript",
            success=False,
            stderr=str(e),
            returncode=1,
        )
    finally:
        try:
            os.unlink(temp_path)
        except OSError as exc:
            note_failure("__init__:L172", exc)


# --- Unified Dispatcher -----------------------------------------------------

LANGUAGE_RUNNERS = {
    "python": run_python,
    "py": run_python,
    "rust": run_rust,
    "rs": run_rust,
    "go": run_go,
    "golang": run_go,
    "bash": run_bash,
    "sh": run_bash,
    "shell": run_bash,
    "javascript": run_javascript,
    "js": run_javascript,
    "node": run_javascript,
}


def run_code(language: str, code: str, args: list[str] = None) -> RunResult:
    """Dispatch code execution to the appropriate language runner."""
    runner = LANGUAGE_RUNNERS.get(language.lower())
    if not runner:
        return RunResult(
            language=language,
            success=False,
            stderr=f"Unsupported language: {language}. "
                    f"Supported: {sorted(set(LANGUAGE_RUNNERS.keys()))}",
            returncode=1,
        )

    if language.lower() in ("bash", "sh", "shell"):
        return runner(code)
    return runner(code, args)


def supported_languages() -> list[str]:
    """Return list of supported languages."""
    return sorted(set(
        k for k in LANGUAGE_RUNNERS
        if len(k) > 2  # Skip short aliases
    ))


# --- CLI ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Azazael Multi-Language Interpreter")
    parser.add_argument("language", help="Language: python, rust, go, bash, javascript")
    parser.add_argument("code", help="Code to execute (or '-' for stdin)")
    parser.add_argument("args", nargs="*", help="Arguments to pass to the program")
    args = parser.parse_args()

    code = args.code
    if code == "-":
        import sys
        code = sys.stdin.read()

        result = run_code(args.language, code, args.args)

        if result.success:
            print(result.stdout, end="")
    else:
        print(f"[{result.language}] Error:", file=sys.stderr)
        print(result.stderr, end="", file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
