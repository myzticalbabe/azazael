"""G1 test for src/eve_unleashed/cradle.py.

The cradle must be safe on an empty directory (nothing adopted, nothing
failed) and its helpers must keep their contracts: a free port is an
int, runner discovery returns a list. Heavy sidecar probes stay out of
the gate; the live Qwen3-4b adoption is recorded in the committed
receipt, not re-run here.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed import cradle


def test_empty_cradle_adopts_nothing(tmp_path):
    summary = cradle.adopt_cradle(tmp_path)
    assert summary["adopted"] == [] and summary["failed"] == []


def test_helpers_keep_contracts():
    port = cradle._free_port()
    assert isinstance(port, int) and 1024 <= port <= 65535
    cands = cradle._llama_server_candidates()
    assert isinstance(cands, list)
    assert all(Path(c).is_file() for c in cands)
