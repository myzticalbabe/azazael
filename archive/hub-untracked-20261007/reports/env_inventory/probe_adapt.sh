#!/usr/bin/env bash
# Report which interpreter can actually import the self-adaptation stack.
for p in /usr/bin/python3 /usr/bin/python3.13 /usr/local/bin/python3.14; do
  [ -x "$p" ] || continue
  "$p" - "$p" <<'PY'
import importlib, sys
mods = ["torch","transformers","gymnasium","stable_baselines3","peft","trl",
        "datasets","sentence_transformers","numpy","networkx","igraph","kuzu",
        "chromadb","llama_cpp","onnxruntime"]
got, missing = [], []
for m in mods:
    try:
        importlib.import_module(m); got.append(m)
    except Exception:
        missing.append(m)
print(f"{sys.argv[1]}  py={sys.version.split()[0]} gil={getattr(sys,'_is_gil_enabled',lambda:True)()}")
print(f"  OK({len(got)}): {','.join(got) or '-'}")
print(f"  MISSING({len(missing)}): {','.join(missing)}")
PY
done
