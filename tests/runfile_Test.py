"""Tests for tools/runfile.py — identification by magic, and honest runner verdicts.

Fixtures are built from the format specifications' own field layouts (ELF e_machine
at 0x12, PE's e_lfanew at 0x3C, class-file major at offset 6), not from files this
machine happened to contain, so a test failure means the detector is wrong rather
than that the corpus changed.
"""

from __future__ import annotations

import json
import struct
import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "runfile.py"
sys.path.insert(0, str(TOOL.parent))
import runfile  # noqa: E402


def make_elf(path: Path, machine: int = 0x3E) -> Path:
    # e_ident is 16 bytes; e_type sits at 16..18 and e_machine at 18..20.
    header = (b"\x7fELF" + b"\x02\x01\x01\x00" + b"\x00" * 8
              + struct.pack("<H", 2) + struct.pack("<H", machine) + b"\x00" * 44)
    path.write_bytes(header)
    return path


def make_pe(path: Path, machine: int = 0x8664) -> Path:
    data = bytearray(0x200)
    data[0:2] = b"MZ"
    data[0x3C:0x40] = struct.pack("<I", 0x80)
    data[0x80:0x84] = b"PE\0\0"
    data[0x84:0x86] = struct.pack("<H", machine)
    path.write_bytes(bytes(data))
    return path


def make_java_class(path: Path, major: int = 61) -> Path:
    path.write_bytes(b"\xca\xfe\xba\xbe" + struct.pack(">HH", 0, major) + b"\x00" * 16)
    return path


def _write(path: Path, blob: bytes) -> Path:
    """Write and return the PATH. `blob.append(path) or path` would return an int:
    write_bytes yields a byte count, which is truthy, so `or` never reaches `path`."""
    path.write_bytes(blob)
    return path


@pytest.mark.parametrize("builder,expected", [
    (lambda p: make_elf(p), "ELF"),
    (lambda p: make_pe(p), "PE"),
    (lambda p: make_java_class(p), "Java class"),
    (lambda p: _write(p, b"\xcf\xfa\xed\xfe" + b"\x00" * 12), "Mach-O"),
    (lambda p: _write(p, b"\0asm\x01\x00\x00\x00"), "WebAssembly"),
    (lambda p: _write(p, b"#!/usr/bin/env python3\nprint(1)\n"), "script"),
    (lambda p: _write(p, b"just some prose\n"), "unknown"),
])
def test_identification_by_magic(tmp_path: Path, builder, expected: str) -> None:
    assert runfile.identify(str(builder(tmp_path / "f.bin"))).name == expected


def test_elf_arch_is_read_from_the_header(tmp_path: Path) -> None:
    elf = make_elf(tmp_path / "a.out", machine=0xB7)
    assert runfile.identify(str(elf)).arch == "aarch64"


def test_class_magic_is_not_confused_with_macho_fat(tmp_path: Path) -> None:
    """0xCAFEBABE is shared; the class-file major range (45..70) disambiguates."""
    assert runfile.identify(str(make_java_class(tmp_path / "A.class"))).name == "Java class"
    fat = tmp_path / "fat.bin"
    fat.write_bytes(b"\xca\xfe\xba\xbe" + struct.pack(">HH", 0, 0) + b"\x00" * 8)
    assert runfile.identify(str(fat)).name == "Mach-O fat"


def test_pe_plan_is_native_on_windows_or_needs_wine_elsewhere(tmp_path: Path) -> None:
    pe = make_pe(tmp_path / "app.exe")
    _ident, step = runfile.plan(str(pe))
    if sys.platform == "win32":
        assert step.verdict == "native", step
        assert step.argv[0].endswith("app.exe")
    else:
        assert step.verdict in ("bridge", "no_runner"), step


def test_elf_plan_names_wsl_as_the_bridge_on_windows(tmp_path: Path) -> None:
    elf = make_elf(tmp_path / "binary")
    _ident, step = runfile.plan(str(elf))
    if sys.platform == "win32":
        if runfile.runner_path("wsl"):
            assert step.verdict == "bridge"
            assert step.runner == "wsl"
            assert "--exec" in step.argv
        else:
            # the honest path: a named absence, never a bare "not executable"
            assert step.verdict == "no_runner"
            assert "WSL" in step.note
    else:
        assert step.verdict in ("native", "no_runner")


def test_shebang_routes_to_its_interpreter_or_names_the_gap(tmp_path: Path) -> None:
    script = tmp_path / "job"
    script.write_bytes(b"#!/usr/bin/env python3\nprint('hi')\n")
    _ident, step = runfile.plan(str(script))
    assert step.verdict in ("bridge", "no_runner"), step
    if step.verdict == "bridge":
        assert str(script) in step.argv
    else:
        assert "python3" in step.note


def test_data_is_reported_as_data_not_as_a_failure(tmp_path: Path) -> None:
    doc = tmp_path / "notes.txt"
    doc.write_bytes(b"plain text, no magic\n")
    _ident, step = runfile.plan(str(doc))
    assert step.verdict == "not_executable"


def test_json_verdict_is_machine_readable(tmp_path: Path) -> None:
    pe = make_pe(tmp_path / "app.exe")
    out = subprocess.run([sys.executable, str(TOOL), "--json", str(pe)],
                         capture_output=True, text=True, check=False, timeout=60)
    assert out.returncode == 0, out.stderr
    payload = json.loads(out.stdout)
    assert payload["format"] == "PE"
    assert payload["verdict"] in ("native", "bridge", "no_runner")


def test_list_reports_every_runner_with_a_path_or_missing() -> None:
    rows = runfile.list_runners()
    names = {row[0] for row in rows}
    assert {"wsl", "wine", "dotnet", "java"} <= names
    for _name, found, _unlocks in rows:
        assert found == "MISSING" or Path(found).exists()
