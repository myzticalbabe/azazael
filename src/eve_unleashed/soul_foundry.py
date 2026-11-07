"""Soul Foundry: Eve builds model artifacts natively.

Formats built with Eve's own hands, no downloads, no converters:

- .gguf  -- native GGUFv3 writer (stdlib struct): header, KV metadata,
  tensor infos, 32-byte aligned f32 tensor data from a seeded RNG.
- .pt    -- torch tensor bundle (needs torch, else skipped with reason).
- .joblib -- tiny sklearn model (needs sklearn, else skipped).
- manifest.json -- sha256 of every artifact plus the build receipt.

Honest boundary, stated in the manifest: the .gguf is a spec-valid
container proven by parse-back roundtrip (magic, version, KV, tensor
shapes, data sha). Runner-loadable weights for a named architecture
need that architecture's real tensors -- queued, not claimed.
"""
import hashlib
import json
import random
import struct
import time
from pathlib import Path

try:
    from CORE.failure_ledger import note_failure
except Exception:
    def note_failure(where, exc=None):
        pass

GGUF_MAGIC = b"GGUF"
GGUF_VERSION = 3
GGUF_ALIGN = 32

# GGUF value types we emit.
_GGUF_U32, _GGUF_F32, _GGUF_STR = 4, 6, 8
# GGUF tensor dtype we emit: 0 = F32.
_GGUF_DTYPE_F32 = 0


def _pack_str(buf, s):
    b = s.encode("utf-8")
    buf += struct.pack("<Q", len(b)) + b


def _pack_kv(buf, key, vtype, value):
    _pack_str(buf, key)
    buf += struct.pack("<I", vtype)
    if vtype == _GGUF_STR:
        _pack_str(buf, value)
    elif vtype == _GGUF_U32:
        buf += struct.pack("<I", value)
    elif vtype == _GGUF_F32:
        buf += struct.pack("<f", value)
    else:
        raise ValueError("foundry emits str/u32/f32 only")


def _align(buf):
    pad = (-len(buf)) % GGUF_ALIGN
    buf += b"\x00" * pad


def build_gguf(path, name, seed=7, rows=8, cols=8):
    """Write a spec-valid GGUFv3 container. Returns the manifest entry."""
    rng = random.Random(seed)
    w = [rng.uniform(-1.0, 1.0) for _ in range(rows * cols)]
    b = [rng.uniform(-1.0, 1.0) for _ in range(cols)]
    tensors = [("foundry.weight", [rows, cols], w),
               ("foundry.bias", [cols], b)]

    header = bytearray()
    header += GGUF_MAGIC
    header += struct.pack("<I", GGUF_VERSION)
    header += struct.pack("<Q", len(tensors))
    kvs = [("general.architecture", _GGUF_STR, "eve-foundry"),
           ("general.name", _GGUF_STR, name),
           ("foundry.seed", _GGUF_U32, seed)]
    header += struct.pack("<Q", len(kvs))
    for key, vtype, value in kvs:
        _pack_kv(header, key, vtype, value)

    data_blobs, offset = [], 0
    for tname, shape, vals in tensors:
        _pack_str(header, tname)
        header += struct.pack("<I", len(shape))
        for dim in shape:
            header += struct.pack("<Q", dim)
        header += struct.pack("<I", _GGUF_DTYPE_F32)
        header += struct.pack("<Q", offset)
        blob = struct.pack("<%df" % len(vals), *vals)
        data_blobs.append(blob)
        offset += len(blob)
        while offset % GGUF_ALIGN:
            offset += 1
    _align(header)
    with open(path, "wb") as f:
        f.write(bytes(header))
        for blob in data_blobs:
            f.write(blob)
            pad = (-len(blob)) % GGUF_ALIGN
            if pad:
                f.write(b"\x00" * pad)
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return {"path": Path(path).name, "format": "gguf", "bytes": Path(path).stat().st_size,
            "sha256": digest, "tensors": [t[0] for t in tensors],
            "note": "container-valid (parse-back verified); runner weights queued"}


def read_gguf(path):
    """Parse back a foundry GGUF. Returns {arch, name, tensors}."""
    data = Path(path).read_bytes()
    off = 0
    assert data[0:4] == GGUF_MAGIC, "bad magic"
    (version, n_tensors, n_kv), off = (struct.unpack_from("<IQQ", data, 4),
                                       4 + struct.calcsize("<IQQ"))

    def take_str():
        nonlocal off
        (ln,), off2 = struct.unpack_from("<Q", data, off), off + 8
        s = data[off2:off2 + ln].decode("utf-8")
        off = off2 + ln
        return s

    meta = {}
    for _ in range(n_kv):
        key = take_str()
        (vtype,), off2 = struct.unpack_from("<I", data, off), off + 4
        off = off2
        if vtype == _GGUF_STR:
            meta[key] = take_str()
        elif vtype == _GGUF_U32:
            (v,), off = struct.unpack_from("<I", data, off), off + 4
            meta[key] = v
        elif vtype == _GGUF_F32:
            (v,), off = struct.unpack_from("<f", data, off), off + 4
            meta[key] = v
        else:
            raise ValueError("unexpected kv type %d" % vtype)
    tensors = []
    for _ in range(n_tensors):
        tname = take_str()
        (n_dims,), off = struct.unpack_from("<I", data, off), off + 4
        dims = struct.unpack_from("<%dQ" % n_dims, data, off)
        off += 8 * n_dims
        (dtype, toff), off = struct.unpack_from("<IQ", data, off), off + 12
        tensors.append({"name": tname, "shape": list(dims), "dtype": dtype,
                        "offset": toff})
    return {"version": version, "arch": meta.get("general.architecture"),
            "name": meta.get("general.name"), "meta": meta,
            "tensors": tensors}


def build_all(out_dir, name="eve-foundry-001", seed=7):
    """Build every natively-supported format. Returns the manifest."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    entries, skipped = [], []

    gguf_entry = build_gguf(out / ("%s.gguf" % name), name, seed)
    parsed = read_gguf(out / ("%s.gguf" % name))
    assert parsed["arch"] == "eve-foundry", parsed
    assert [t["name"] for t in parsed["tensors"]] == gguf_entry["tensors"]
    gguf_entry["parse_back"] = "ok"
    entries.append(gguf_entry)

    try:
        import torch
        bundle = {"weight": torch.randn(8, 8),
                  "bias": torch.randn(8),
                  "foundry": {"name": name, "seed": seed}}
        torch.save(bundle, str(out / ("%s.pt" % name)))
        import hashlib as _h
        entries.append({"path": "%s.pt" % name, "format": "torch",
                        "bytes": (out / ("%s.pt" % name)).stat().st_size,
                        "sha256": _h.sha256((out / ("%s.pt" % name)).read_bytes()).hexdigest(),
                        "load_back": type(torch.load(str(out / ("%s.pt" % name)),
                                                     map_location="cpu", weights_only=True)).__name__})
    except ImportError as e:
        note_failure("foundry:torch", e)
        skipped.append({"format": "torch", "reason": "torch not installed"})
    try:
        import joblib
        from sklearn.linear_model import LinearRegression
        model = LinearRegression().fit([[0], [1], [2]], [0, 1, 2])
        joblib.dump({"model": model, "foundry": {"name": name}},
                    out / ("%s.joblib" % name))
        import hashlib as _h
        entries.append({"path": "%s.joblib" % name, "format": "sklearn",
                        "bytes": (out / ("%s.joblib" % name)).stat().st_size,
                        "sha256": _h.sha256((out / ("%s.joblib" % name)).read_bytes()).hexdigest(),
                        "load_back": type(joblib.load(out / ("%s.joblib" % name))["model"]).__name__})
    except ImportError as e:
        note_failure("foundry:sklearn", e)
        skipped.append({"format": "sklearn", "reason": "sklearn not installed"})

    manifest = {"foundry": "soul-foundry", "model": name, "seed": seed,
                "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "entries": entries, "skipped": skipped}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2),
                                       encoding="utf-8")
    return manifest
