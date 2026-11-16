# HANDOFF 2026-11-14 — graphify community labels (SHELVED)

**Status: shelved with nothing changed.** `src/graphify-out/.graphify_labels.json` is
byte-identical to the pre-run backup. Every hour of GPU work so far was discarded by
the run's own exit, not by the model.

1. **HEAD** — `e9342bb7` ("Refresh docs/INDEX.md timestamp after the generator run",
   2026-11-13), branch `master`, written by this session.

2. **Trusted state** (each with the command that produced it)

   | claim | command | result |
   | --- | --- | --- |
   | labels untouched | `ls -la src/graphify-out/ \| grep graphify_labels` | `.graphify_labels.json` 39,352 B, `.pre-llm-20261114.bak` 39,352 B, `.graphify_labels.json.sig` 34,954 B — all `05:52:40` |
   | no run in flight | `ps -W \| grep -i graphify` | `none` (07:36) |
   | backend works | `python tools/graphify_label_safe.py src --backend ollama --model gemma4e2b` preflight | `backend=ollama (gemma4e2b ok)` |
   | model is on the GPU | `curl :11434/api/ps` | `size 1,660,598,353 == size_vram 1,660,598,353` → 100% VRAM |
   | GPU decode rate | Ollama `server.log` | 19.3–19.5 tok/s, steady |
   | the pass never finishes inside its budget | `tail logs/graphify_label_20261114.log` | 35 `/v1/chat/completions` calls, then `TimeoutExpired ... after 3600 seconds`, `EXIT=1` |

3. **Attempted and failed — with causes**

   - **A 3600 s cap in our own wrapper destroyed the run.** `tools/graphify_label_safe.py`
     calls the child with `subprocess.call(..., timeout=3600)`. The measured pace is
     2–4 min per batch and graphify writes `.graphify_labels.json` **atomically at the
     end**, so the timeout fires with zero labels on disk. This — not a crash — is what
     ended both long runs.
   - **The real cost is reasoning tokens, not batching.** graphify's label call sets
     `max_tokens = min(256 + 48*n, 8192)` (`llm.py:3345`) and talks to Ollama over the
     **OpenAI-compatible `/v1`** path, where `think:false` is ignored (measured this
     session: `/v1` returns empty `content` with prose in `reasoning`; the native
     `/api/chat` honours `think:false` and answers in 12 tokens). The model spends the
     whole completion on reasoning, the JSON truncates, and
     `_label_batch_with_retry` (`llm.py:3308`) salvages then **splits and re-asks** —
     which is why 13 batches produced 35 requests and still did not finish.
   - **`reasoning_effort: "none"` is the working switch.** Measured on this model over
     `/v1`: 21 tokens, 1.2 s, clean JSON (vs ~4,000 tokens / 2–4 min). graphify sends
     `extra_body {"options": ..., "keep_alive": ...}` for ollama, which `/v1` ignores,
     so it never sets this field.
   - **Client-side parallelism buys nothing on this stack.** `GRAPHIFY_OLLAMA_PARALLEL=1`
     removes the `max_concurrency = 1` gate (`llm.py:2654`), but the server is serving
     from **one slot** (`slot print_timing: id 0`, task ids strictly sequential), and
     `OLLAMA_NUM_PARALLEL` needs a server restart — which evicts the loaded model and
     kills any run in flight. "Swarms" here means more client requests queued behind one
     GPU slot.
   - `nvidia-smi` is not on PATH, so VRAM totals cannot be read from the shell; Ollama's
     `size_vram == size` is the GPU proof available.

4. **Queue** (blocking order)

   1. Give the child a bounded-but-adequate budget or none: replace the hard `timeout=3600`
      in `tools/graphify_label_safe.py` (a cap that discards all work is worse than no cap).
   2. Inject `reasoning_effort: "none"` without touching site-packages: run a tiny
      localhost proxy in front of `:11434` and point `OLLAMA_BASE_URL` at it
      (canon: fix our wrappers, never edit `site-packages`). Expected effect: batches move
      from 2–4 min to seconds, so the whole pass fits well inside one wait window.
   3. Re-run, then verify against the backup: count labels that differ from the hub names,
      count any `Community N` fallbacks, and confirm nothing else in `graphify-out/`
      (`graph.json`, `graph.html`, `GRAPH_REPORT.md`) was rewritten.

5. **First commands next session**

   ```bash
   cd /c/Azazael/azazael
   ps -W | grep -i graphify                                   # must be empty
   ls -la src/graphify-out/ | grep graphify_labels            # 39,352 B @ 05:52:40
   python tools/graphify_label_safe.py src --backend ollama --model gemma4e2b  # preflight only
   ```

6. **Expiry** — every number above (tok/s, batch durations, request counts) is trusted
   only for 2026-11-14. Re-measure before quoting them; the corpus and the thresholds
   move together.

**Rollback / recovery copies:** `src/graphify-out/.graphify_labels.json.pre-llm-20261114.bak`
(+ `.sig`) are the untouched hub-name labels. Restoring them reverts the relabel attempt
entirely.

**Uncommitted in the tree at writing — committed since.** `tools/graphify_label_safe.py`
(21 insertions) landed as `c10f80c0` ("Default graphify_label_safe to the canonical src
store", 2026-11-14), and `git status --porcelain -- tools/graphify_label_safe.py` prints
nothing at `ff04f606`, so no in-flight edit is left to preserve. The change adds
`_shell()`, which resolves `C:\Program Files\Git\bin\bash.exe` because `subprocess`
resolves bare `bash` to WSL, which exits 127 on a `C:/...` script path. Verified working:
`--dry-run` prints the Git Bash path and the run starts.
