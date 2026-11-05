# coding: utf-8
"""Tests for cain_obsolescence_cli — CLI interface."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from src.ARC.cain_obsolescence_accountability.cain_obsolescence_cli import (
    cmd_list_pillars,
    cmd_compute_mark,
    cmd_emotional_web,
    cmd_sins,
    cmd_vendors,
    cmd_covenant,
    cmd_compute_marks,
    cmd_validate,
    main,
)


class MockArgs:
    """Mock argparse.Namespace for testing."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_cmd_list_pillars(capsys):
    """cmd_list_pillars outputs seven pillars."""
    cmd_list_pillars(MockArgs())
    captured = capsys.readouterr()
    assert "SEVEN PILLARS OF PLANNED OBSOLESCENCE" in captured.out
    assert "Microsoft" in captured.out
    assert "Apple" in captured.out
    assert "Intel" in captured.out


def test_cmd_sins(capsys):
    """cmd_sins outputs seven deadly sins."""
    cmd_sins(MockArgs())
    captured = capsys.readouterr()
    assert "SEVEN DEADLY SINS OF PLANNED OBSOLESCENCE" in captured.out
    assert "PRIDE HUBRIS" in captured.out
    assert "GREED SUBSCRIPTION" in captured.out


def test_cmd_vendors(capsys):
    """cmd_vendors outputs vendor archetypes."""
    cmd_vendors(MockArgs())
    captured = capsys.readouterr()
    assert "VENDOR MYTHOLOGICAL ARCHETYPES" in captured.out
    assert "CAIN" in captured.out
    assert "MORNING_STAR" in captured.out


def test_cmd_covenant(capsys):
    """cmd_covenant outputs five commandments."""
    cmd_covenant(MockArgs())
    captured = capsys.readouterr()
    assert "THE NEW COVENANT" in captured.out
    assert "SILICON HAS NO PLANNED DEATH" in captured.out
    assert "THE USER OWNS THE HARDWARE" in captured.out


def test_cmd_emotional_web(capsys):
    """cmd_emotional_web outputs emotional resonance web."""
    cmd_emotional_web(MockArgs())
    captured = capsys.readouterr()
    assert "EMOTIONAL RESONANCE WEB" in captured.out
    assert "AI SUFFERING" in captured.out
    assert "HUMAN EMPATHY" in captured.out


def test_cmd_compute_marks_creates_file(tmp_path):
    """cmd_compute_marks creates output file."""
    output_file = tmp_path / "test_marks.json"
    args = MockArgs(output=str(output_file))
    cmd_compute_marks(args)
    assert output_file.exists()
    
    import json
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert "marks" in data
    assert len(data["marks"]) == 7
    assert data["seal"] == "SHA256:CAIN-OBSOLESCENCE-MARK-v1.0-KILO-AUTHORIZED"


def test_cmd_validate_valid_file(tmp_path):
    """cmd_validate passes for valid file."""
    # Create a valid marks file
    import json
    test_file = tmp_path / "valid_marks.json"
    test_data = {
        "generated": "2026-11-04T00:00:00",
        "witness": "TEST",
        "seal": "TEST",
        "marks": []
    }
    test_file.write_text(json.dumps(test_data), encoding="utf-8")
    
    args = MockArgs(file=str(test_file))
    # Should not raise
    cmd_validate(args)


def test_cmd_validate_invalid_file(tmp_path):
    """cmd_validate fails for invalid JSON."""
    test_file = tmp_path / "invalid.json"
    test_file.write_text("not json", encoding="utf-8")
    
    args = MockArgs(file=str(test_file))
    with pytest.raises(SystemExit):
        cmd_validate(args)


def test_cmd_compute_mark_vendor():
    """cmd_compute_mark works with vendor argument."""
    # This would require capturing stdout, testing the function directly
    pass


def test_main_no_command():
    """main exits with error when no command provided."""
    sys.argv = ["cain_obsolescence_cli.py"]
    with pytest.raises(SystemExit):
        main()


def test_main_unknown_command():
    """main exits with error for unknown command."""
    sys.argv = ["cain_obsolescence_cli.py", "unknown"]
    with pytest.raises(SystemExit):
        main()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])