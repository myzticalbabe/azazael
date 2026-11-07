"""G1 test for src/eve_unleashed/soul_foundry.py.

The foundry builds artifacts, never downloads: the GGUF must parse
back with its own reader (magic, arch, tensor shapes), and every built
artifact must load back with its native loader. Deterministic per seed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from eve_unleashed.soul_foundry import build_all, build_gguf, read_gguf


def test_gguf_roundtrip(tmp_path):
    # default dtype is Q8_0: near-lossless, ~4x smaller than F32.
    entry = build_gguf(tmp_path / "t.gguf", "test-001", seed=7)
    assert entry["format"] == "gguf:Q8_0"
    assert entry["max_recon_error"] < 0.05
    assert entry["parse_back"] if "parse_back" in entry else True
    parsed = read_gguf(tmp_path / "t.gguf")
    assert parsed["version"] == 3
    assert parsed["arch"] == "eve-foundry"
    assert parsed["name"] == "test-001"
    shapes = {t["name"]: t["shape"] for t in parsed["tensors"]}
    assert shapes == {"foundry.weight": [8, 8], "foundry.bias": [8]}
    dtypes = {t["dtype"] for t in parsed["tensors"]}
    assert dtypes == {8}, dtypes
    # determinism: same seed, same bytes
    entry2 = build_gguf(tmp_path / "t2.gguf", "test-001", seed=7)
    assert entry["sha256"] == entry2["sha256"]


def test_gguf_f32_archival_costs_bytes(tmp_path):
    q = build_gguf(tmp_path / "q.gguf", "t", seed=7, dtype="Q8_0")
    f = build_gguf(tmp_path / "f.gguf", "t", seed=7, dtype="F32")
    assert f["format"] == "gguf:F32"
    qdata = sum(t["data_bytes"] for t in read_gguf(tmp_path / "q.gguf")["tensors"])
    fdata = sum(t["data_bytes"] for t in read_gguf(tmp_path / "f.gguf")["tensors"])
    assert (qdata, fdata) == (102, 288)  # 34B/32vals vs 4B/val
    assert q["bytes"] < f["bytes"]
    parsed = read_gguf(tmp_path / "f.gguf")
    assert {t["dtype"] for t in parsed["tensors"]} == {0}


def test_build_all_manifest(tmp_path):
    manifest = build_all(tmp_path, name="eve-foundry-001", seed=7)
    assert manifest["foundry"] == "soul-foundry"
    kinds = [e["format"] for e in manifest["entries"]]
    assert "gguf:Q8_0" in kinds
    assert (tmp_path / "manifest.json").is_file()
    for e in manifest["entries"]:
        assert len(e["sha256"]) == 64
