# SHARDEX

Shard tooling: build a shard, render its mesh, and check the result rather than
trusting a digest that was written by the same code that wrote the file.

The full documentation lives in **[SHARDEX.md](SHARDEX.md)**; this file exists so
that a repository page has something to render.

## What ships here

| command | module | what it does |
|---|---|---|
| `shardex` | `shardex.py` | builds and inspects a shard |
| `shardex-mesh` | `meshscene.py` | renders the mesh scene for a shard |
| `shardex-transubstantiate` | `transubstantiate.py` | converts between shard representations |

`ops.py` ships as a module because `meshscene.py` imports it directly; omitting it
would break all three commands at import time.

## Requirements beyond pip

The mesh renderer drives a browser, so it needs **Node with puppeteer and a Chrome
install**. That cannot be expressed in `dependencies`, and claiming an empty
dependency set while silently requiring a browser is the kind of metadata lie this
tree has already been burned by. The Python side is standard library only.

## Quickstart

```bash
pip install .
shardex --help
```

## License

This project is licensed under the **Soul Forge License v1.0** — a covenant, not a
contract. The full text is in [LICENSE](LICENSE).

You may use, copy, modify, merge, publish, distribute, sublicense and/or
sell copies of the software, provided you keep the maker's mark intact,
do not wrap the code in DRM or obfuscation, and return your modifications
under this same license.

```
    Soul Forge License v1.0
    Author: myzticalbabe
    Forged: 2026-11-14
    Source: https://github.com/myzticalbabe/Project_SHARDEX
    Spirit: "Code is crystallized intention. Tend the fire."
```

Author: myzticalbabe · Forged: 2026-11-14 · Spirit: "Code is crystallized intention. Tend the fire."
