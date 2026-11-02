# SHARDEX Community Shard Contribution Protocol
**Date:** November 2, 2026  
**Task:** SHARDEX-COMMUNITY-SHARDS (board_id=47302)  
**Deliverable:** docs/SHARDEX_COMMUNITY.md

---

## Overview

Design a community-driven shard contribution system for SHARDEX where:
- Anyone can mirror + shatter a game
- Publish shard ID for others to forge + verify
- No gatekeeping - open contribution
- Verification through cryptographic proofs

---

## Core Principles

1. **Permissionless** - No approval needed to contribute
2. **Verifiable** - Cryptographic proofs for every shard
3. **Reproducible** - Same game + same tool = same shards
4. **Attributable** - Contributors get credit
5. **Decentralized** - No central registry required

---

## Shard Format

### Shard Structure
```
shard/
├── manifest.json          # Shard metadata + hashes
├── assets/
│   ├── sprites/          # PNG/WebP, hashed
│   ├── audio/            # OGG/MP3, hashed
│   ├── maps/             # Tiled JSON, hashed
│   └── scripts/          # Lua/JS, hashed
├── code/
│   ├── engine/           # Core game logic
│   ├── entities/         # Entity definitions
│   └── systems/          # Game systems
└── proofs/
    ├── build.proof       # Reproducible build proof
    └── content.proof     # Content hash proofs
```

### Manifest Schema
```json
{
  "shard_id": "sha256_of_manifest",
  "version": 1,
  "game": {
    "title": "Space Arena",
    "original_hash": "sha256_of_original_game",
    "source_url": "https://example.com/game.zip"
  },
  "contributor": {
    "name": "community_member",
    "pubkey": "ed25519_pubkey",
    "signature": "ed25519_signature_of_manifest"
  },
  "shards": [
    {
      "index": 0,
      "name": "core",
      "hash": "sha256",
      "size": 1048576,
      "files": 42
    }
  ],
  "total_size": 5242880,
  "total_files": 156,
  "created": "2026-11-02T12:00:00Z",
  "tool_version": "shardex-v1.0.0"
}
```

---

## Contribution Protocol

### 1. Mirror (Download)
```bash
shardex mirror https://example.com/game.zip
# Downloads, verifies original hash, stores in local cache
```

### 2. Shatter (Shard)
```bash
shardex shatter game.zip --output ./shards/space_arena/
# Analyzes game structure
# Splits into logical shards (core, assets, levels, etc.)
# Generates manifest + proofs
# Outputs shard directory with manifest.json
```

### 3. Forge (Verify + Package)
```bash
shardex forge ./shards/space_arena/
# Verifies all hashes match manifest
# Reproducibly builds from source
# Generates build.proof (reproducible build)
# Packages as .shardex file for distribution
```

### 4. Publish
```bash
shardex publish ./shards/space_arena/ --registry community
# Uploads to community registry (IPFS, GitHub, etc.)
# Announces via community channels
# Others can now verify + use
```

### 4. Verify (Anyone Can Do This)
```bash
shardex verify shardex://community/space_arena/v1.0.0
# Downloads manifest + shards
# Verifies all hashes
# Reproducibly builds from source
# Confirms content matches original
```

---

## Verification System

### Three-Layer Verification

#### Layer 1: Content Hashes
- Every file SHA-256 hashed
- Manifest lists all file hashes
- Tamper-evident: any change detected

#### Layer 2: Reproducible Build
- Deterministic build from source
- Same tool + same source = identical output
- `build.proof` records: tool version, env, timestamps, output hashes

#### Layer 3: Cryptographic Attestation
- Contributor signs manifest with Ed25519 key
- Signature proves authorship
- Community can verify signature

### Verification Command Output
```
$ shardex verify shardex://community/space_arena/v1.0.0

[✓] Manifest signature valid (contributor: alice)
[✓] All 156 file hashes match manifest
[✓] Reproducible build successful (shardex-v1.0.0)
[✓] Build proof valid (deterministic output confirmed)
[✓] Original game hash matches: a1b2c3d4...
[✓] All shards internally consistent

VERIFICATION PASSED - Shard is authentic and reproducible
```

---

## Community Registry

### No Central Authority
- Registry is a **distributed index** (IPFS, Git, DHT)
- Anyone can run a registry mirror
- Entries are signed manifests
- No approval process - publish directly

### Registry Entry Format
```json
{
  "shard_id": "sha256",
  "manifest_ipfs": "Qm...",
  "shards_ipfs": ["Qm...", "Qm..."],
  "manifest_signature": "ed25519...",
  "contributor_pubkey": "ed25519...",
  "published": "2026-11-02T12:00:00Z",
  "tags": ["arcade", "multiplayer", "retro"],
  "description": "Space Arena - 2 player arena shooter"
}
```

### Discovery
- Search by tag, contributor, game title
- Filter by tool version compatibility
- Sort by verification status, popularity

---

## Contribution Workflow

### For Contributors
1. **Find a game** you want to shard
2. **Mirror** it locally
3. **Shatter** it into shards
4. **Forge** verification proofs
5. **Publish** to community registry
6. **Announce** in community channels

### For Verifiers
1. **Browse** registry for interesting shards
2. **Verify** any shard with one command
3. **Report** issues if verification fails
4. **Use** verified shards in projects

### For Maintainers (Tool Authors)
1. **Update** shardex tool with new features
2. **Maintain** backward compatibility
3. **Curate** verification standards
4. **Resolve** disputes (rare, math-based)

---

## Quality Standards

### Minimum Viable Shard
- [ ] Valid manifest.json with all required fields
- [ ] All file hashes match manifest
- [ ] Reproducible build passes
- [ ] Contributor signature valid
- [ ] Original game hash documented

### Recommended
- [ ] Multiple shards for large games
- [ ] Build proof includes environment lockfile
- [ ] Content proof includes asset catalog
- [ ] Tags for discoverability
- [ ] Human-readable description

### Gold Standard
- [ ] Cross-platform build verified (Windows + Linux + macOS)
- [ ] Deterministic build in CI/CD
- [ ] Multiple independent verifications
- [ ] Community endorsements (signatures from verifiers)

---

## Dispute Resolution

### If Verification Fails
1. Verifier publishes failure report (signed)
2. Contributor can:
   - Fix and republish (new version)
   - Provide additional proof
   - Accept and withdraw
3. Community evaluates evidence
3. Registry updates status

### Evidence Standards
- All evidence must be cryptographically verifiable
- Build logs must be reproducible
- Hash mismatches are objective facts
- No subjective judgments

---

## Tooling Requirements

### Core CLI (`shardex`)
```bash
shardex mirror <url>                    # Download + verify
shardex shatter <input> --output <dir>  # Create shards
shardex forge <shard_dir>               # Verify + package
shardex publish <shard_dir>             # Publish to registry
shardex verify <shard_ref>              # Full verification
shardex search <query>                  # Registry search
shardex info <shard_ref>                # Show manifest
```

### Registry API (for mirrors)
```
GET  /api/v1/shards                    # List with filters
GET  /api/v1/shards/{id}               # Get manifest
GET  /api/v1/shards/{id}/shards/{idx}  # Get shard data
POST /api/v1/shards                    # Publish (signed)
```

---

## Example: Community Contribution

### Alice Contributes "Space Arena"
```bash
# 1. Mirror
shardex mirror https://archive.org/download/space_arena/space_arena.zip

# 2. Shatter
shardex shatter space_arena.zip --output ./shards/space_arena_v1

# 3. Forge (verifies + builds)
shardex forge ./shards/space_arena_v1

# 4. Publish
shardex publish ./shards/space_arena_v1 --registry community
# Output: Published as shardex://community/space_arena/v1.0.0
```

### Bob Verifies
```bash
shardex verify shardex://community/space_arena/v1.0.0
# [✓] All checks pass
# Bob can now use this shard confidently
```

### Carol Uses in Her Project
```bash
shardex install shardex://community/space_arena/v1.0.0 --target ./my_game/assets/
# Shards downloaded, verified, extracted
```

---

## Governance

### No Central Control
- Protocol defined by open specification
- Tool implementations open source
- Registry mirrors community-operated
- Standards evolve through RFC process

### Versioning
- Semantic versioning for protocol
- Tool versions tracked in manifests
- Backward compatibility guaranteed within major version

### Community Channels
- GitHub Discussions for proposals
- Discord/IRC for real-time
- Mailing list for announcements
- All decisions logged publicly

---

## Implementation Roadmap

### Phase 1: Core Tooling (v1.0)
- [ ] `mirror`, `shatter`, `forge`, `verify` commands
- [ ] Manifest schema + validation
- [ ] Reproducible build system
- [ ] Ed25519 signing/verification
- [ ] SHA-256 hashing pipeline

### Phase 2: Registry (v1.1)
- [ ] IPFS-based registry backend
- [ ] `publish`, `search`, `info` commands
- [ ] Registry mirror protocol
- [ ] Community mirror bootstrap

### Phase 3: Ecosystem (v1.2)
- [ ] CI/CD integration templates
- [ ] Game-specific shatter profiles
- [ ] Verification badges
- [ ] Contributor reputation system

### Phase 4: Scale (v2.0)
- [ ] Distributed registry (DHT)
- [ ] Incremental shard updates
- [ ] Cross-shard dependencies
- [ ] Formal verification integration

---

## Legal & Ethics

### Licensing
- Tool: MIT/Apache-2.0
- Shards: Respect original game licenses
- Contributors retain copyright on their manifests
- Community registry: CC0 for index data

### Attribution
- Original game authors credited in manifest
- Contributors credited for sharding work
- Verifiers acknowledged in verification logs

### Prohibited
- Copyrighted games without permission
- Malicious shards (malware, corrupted data)
- Impersonation (fake signatures)
- Spam/flooding registry

---

## Conclusion

SHARDEX Community Shards enables **permissionless, verifiable, reproducible** game preservation and sharing. By combining cryptographic proofs with reproducible builds, anyone can contribute, anyone can verify, and everyone benefits from a growing library of authentic game shards.

**The protocol is the authority, not any central server.**