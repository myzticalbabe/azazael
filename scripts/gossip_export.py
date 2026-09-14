#!/usr/bin/env python3
"""WSL-side gossip export: dump this env's spine payload to the C: drop dir.

Invoked from Windows: wsl -d <distro> -- python3 /mnt/c/.../gossip_export.py
Never raises (prints {} on failure). Keeps Manson-family separation: this
script only READS local ledger and writes one JSON file.
"""
import json
import sys

sys.path.insert(0, "/mnt/c/Users/clint/azazael/src")
DROP = "/mnt/c/Users/clint/azazael/output/gossip"


def main():
    import logging
    logging.disable(logging.CRITICAL)
    try:
        from CORE.WORMS.expansion.envmesh import env_id_v2
        from CORE import spine_registry as sp
        env = env_id_v2()
        payload = sp.export_spine_gossip()
        import os
        os.makedirs(DROP, exist_ok=True)
        with open(f"{DROP}/{env}.json", "w", encoding="utf-8") as f:
            json.dump({"env": env, "payload": payload}, f)
        print(json.dumps({"success": True, "env": env}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)[:150]}))


if __name__ == "__main__":
    main()
