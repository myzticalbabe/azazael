#!/usr/bin/env python3
"""Shard registry — hand-curated v1 manifest over existing skills and tools.

Each entry names the capability, the repo paths that implement it, the
languages available (in preference order), and the canonical implementation
the router tries first. New shards are added by appending an entry; nothing
moves. Doc-only skill families list ["doc"] — their SHARD.md IS the artifact.
"""

SHARDS: dict = {
    "gateway": {
        "paths": ["gateway-go/main.go", "gateway/src/main.rs"],
        "langs": ["go", "rust"],
        "canonical": "go",
        "notes": "Proven polyglot pair: identical OpenAI-front-end contract, "
                 "two implementations. Template for all future dual-lang shards.",
    },
    "interpreters": {
        "paths": ["src/INTERPRETERS/"],
        "langs": ["python", "go", "rust", "javascript", "powershell", "shell"],
        "canonical": "python",
        "notes": "Runner fleet. Python hosts; every other language executes "
                 "through its dedicated runner module.",
    },
    "skills-core": {
        "paths": ["azazael-conventions", "azazael-testing", "azazael-git",
                  "azazael-sop", "azazael-mandates"],
        "langs": ["doc"],
        "canonical": "doc",
        "notes": "Always-on discipline pack. Doc shard: SKILL.md is the artifact.",
    },
    "skills-inference": {
        "paths": ["azazael-inference*", "azazael-inference-protocol",
                  "azazael-inference-worms"],
        "langs": ["doc", "python"],
        "canonical": "doc",
        "notes": "Inference providers, protocol, worm integrations.",
    },
    "skills-worms": {
        "paths": ["azazael-worms*", "azazael-clusters", "azazael-registry"],
        "langs": ["doc", "python"],
        "canonical": "doc",
        "notes": "Worm registry, cluster system, category families.",
    },
    "skills-devtools": {
        "paths": ["azazael-devtools-*"],
        "langs": ["doc", "javascript"],
        "canonical": "doc",
        "notes": "Chrome DevTools panels; JS snippets run via node_runner.",
    },
    "skills-ops": {
        "paths": ["azazael-sync-*", "azazael-deploy", "azazael-exe-build",
                  "azazael-tool-*"],
        "langs": ["doc", "python", "powershell", "shell"],
        "canonical": "doc",
        "notes": "Sync/deploy/tooling. pwsh+shell secondaries for host tasks.",
    },
    "scripts-ops": {
        "paths": ["scripts/*.py"],
        "langs": ["python", "shell"],
        "canonical": "python",
        "notes": "Ops scripts; shell secondary for WSL/Git-Bash automation.",
    },
}

# Keyword router: task text -> shard name. First match wins; order matters.
SHARD_KEYWORDS: dict = {
    "gateway": ["gateway", "llama-server", "upstream", "chat/completions"],
    "interpreters": ["runner", "go_runner", "rust_runner", "node_runner",
                     "pwsh_runner", "sh_runner", "polyglot"],
    "skills-inference": ["inference", "provider", "nim", "llm"],
    "skills-worms": ["worm", "cluster", "registry"],
    "skills-devtools": ["devtools", "chrome", "lighthouse", "dom"],
    "skills-ops": ["sync", "deploy", "wsl", "kali", "sync_all"],
    "scripts-ops": ["script", "gate", "scanner", "ratchet"],
    "skills-core": [],
}


def route_shard(task: str) -> str:
    """Top-1 router: task text -> shard name (falls back to skills-core)."""
    text = (task or "").lower()
    for shard, keywords in SHARD_KEYWORDS.items():
        for keyword in keywords:
            if keyword and keyword in text:
                return shard
    return "skills-core"


def shard_langs(name: str) -> list:
    """Languages available for a shard (empty list for unknown names)."""
    entry = SHARDS.get(name)
    return list(entry["langs"]) if entry else []
