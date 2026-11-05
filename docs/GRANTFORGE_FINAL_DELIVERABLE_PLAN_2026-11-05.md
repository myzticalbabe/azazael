# GRANTFORGE — final deliverable plan (2026-11-05)

**Deliverable, in one sentence:** a single Windows executable, `grantforge.exe`, that runs a
grant workflow against a **local** LLM (no cloud key, no network) and speaks MCP over stdio so
an AI client can call it as a native tool.

**Plan author:** freebuff lane, HEAD `f779ee78`. Every number below was measured in this
session; the command that produced it is named where the number matters.

---

## 1. What exists, measured — and why it cannot be the deliverable as-is

`src/grantforge/` is 13 modules / 3 199 lines, and it is a **shell**:

| surface | state |
| --- | --- |
| `python -m grantforge --help` | works (typer) — exit 0, banner renders |
| `grantforge/__init__.py` | imports **pydantic, typer, rich, httpx, lxml** before any command runs |
| `discovery/`, `eligibility/`, `compliance/`, `collaboration/`, `export/` | `__init__.py` only — no engine |
| `engine.py`, `schemas.py`, `pipeline.py`, `drafting/sections.py` | real code (93 + 170 + … lines), but nothing constructs an engine |
| `config.py` | `LLM_URL` defaults to `http://127.0.0.1:18090/v1/chat/completions` — **nothing listens there** (`curl` → connect failure) |
| `src/grantforge.spec`, `src/grantforge.nuitka.toml` | PyInstaller spec, Nuitka toml with `enable_plugins = [playwright, transformers, torch, openvino, …]` |
| `src/nuitka-crash-report.xml` | the last build **completed as `exception`** (`BrokenPipeError`, Nuitka 4.2rc2) |
| `dist/` | no `grantforge.exe` anywhere in the tree |

And the machine contradicts the build plan: **no `cl` and no `gcc` on PATH** (VS2022 is
installed, Nuitka can fetch MinGW), **PyInstaller is not installed**, and the disk has
**2.9 GB free (100 % used)**. A Nuitka build that pulls `transformers`/`torch`/`openvino`/
`playwright` cannot fit, and is the exact build that already crashed.

**Conclusion:** the executable cannot be built from the existing import graph. It has to be
built from a stdlib-only core, and the existing package stays as the (aspirational) rich CLI.

## 2. What is already true on this box — the interop target

Measured this session against `http://127.0.0.1:8081` (llama.cpp `llama-server`, b10964):

```
GET  /v1/models            200 in 0.0026 s   -> {"models":[{"name":"…Qwen3-4B-Instruct-2507-abliterated.Q4_K_M.gguf"}]}
POST /v1/chat/completions  200 in <1 s       -> {"choices":[{"message":{"content":"OK! 😊"}}], "usage":{…}}
GET  /props                200 in 0.0047 s
```

Two model-list shapes must be accepted, because two servers are in play on this machine:
llama-server answers `{"models":[{"name":…}]}`, OpenAI-compatible servers answer
`{"data":[{"id":…}]}`. A client that only parses one shape reports "no model" against a
healthy endpoint — the same class of defect as a silent default.

## 3. Architecture of the deliverable

New top-level package **`src/grantforge_native/`** — stdlib only (`urllib`, `json`,
`hashlib`, `argparse`, `http.server` only in tests). It does **not** import `grantforge`,
because that parent package imports pydantic/typer/rich/lxml and would drag ~1 GB of optional
dependency into a binary that must run on a clean box.

```
grantforge.exe
├── llm.py      local-model client: discovery (both shapes), bounded retries,
│               JSON-object extraction, ONE repair attempt that quotes the defect,
│               explicit LLMUnavailable / LLMBadReply (never a silent empty answer)
├── grants.py   the domain, deterministic first:
│               rules -> verdicts, LLM -> only text criteria, and a verdict without a
│               quote from the RFP is DOWNGRADED to `unjudged`
│               review -> codes + fix hints; seal -> sha256 of canonical JSON
├── mcp.py      stdio JSON-RPC 2.0 MCP server (line-delimited), tools:
│               grantforge_doctor | _assess | _draft | _review | _verify
└── cli.py      doctor | models | assess | draft | review | verify | mcp | demo
                every command --json; --offline runs the rule engine with no model
```

**The admissibility rule is the point, not a feature.** A local 4B model will happily invent a
criterion, a deadline, or a citation. So: a model verdict is accepted only with a verbatim
quote from the supplied RFP text; otherwise the row is `unjudged` and the run says so. Drafting
counts fabricated figures (a number absent from the profile/RFP) and marks the section
`unsupported` instead of shipping it. This is the HYPER_EDGE principle applied where it pays:
a claim without its evidence is not a verdict.

## 4. Definition of done — acceptance commands, in order

| # | check | command | expected |
| --- | --- | --- | --- |
| 1 | unit suite | `pytest tests/test_grantforge_native.py -q` | all pass; the fake-server tests prove both model shapes, a 503 retry, the one-repair path, and downgrade-without-quote |
| 2 | offline CLI | `python -m grantforge_native assess --offline --json <rfp> <profile>` | exit 0, rule verdicts, no network touched |
| 3 | live model | `python -m grantforge_native doctor --json` | exit 0, `models: 1+`, `roundtrip_ms` recorded, endpoint + model named |
| 4 | live assess | `python -m grantforge_native assess <rfp> <profile>` | numeric rule rows + at most quote-backed LLM rows; unbacked rows `unjudged` |
| 5 | draft + review | `... draft ... && ... review ...` | review exits 0 with zero `unsupported` sections, or exits 1 naming them |
| 6 | MCP handshake | `printf '{"jsonrpc":"2.0","id":1,"method":"initialize"}\n…' \| grantforge.exe mcp` | one JSON line per request, `tools/list` names 5 tools, no non-JSON byte on stdout |
| 7 | the binary | `dist-native/grantforge.exe doctor --json` | never launched a Python interpreter; exit 0 |

A check that cannot run is reported as `BLOCKED` with its command. It is never a pass.

## 5. Build plan, sized to the disk that actually exists

1. **Nuitka, onefile, stdlib-only.** `--standalone --onefile --python-flag=no_site
   --output-filename=grantforge.exe --assume-yes-for-downloads`. No plugins, no
   `include_packages` beyond the package itself. Expected ~15–25 MB binary; compile temp well
   under the 1.5 GB budget.
2. **Compiler:** none on PATH, so Nuitka must fetch MinGW64 (~150 MB). If the fetch fails,
   fall back to `--mingw64` with the cached toolchain, then to MSVC via `vswhere` (VS2022 is
   installed at `C:/Program Files (x86)/Microsoft Visual Studio/2022`).
3. **If onefile fails:** `--standalone` (directory) is still an executable deliverable; ship
   the directory plus the exact failure for onefile.
4. **Never** re-run the old `grantforge.nuitka.toml` build: its plugin list is the crash that
   already happened. The old spec/toml stay untouched as history; the new build script is
   `tools/build_grantforge_native.py`.
5. The binary is **not committed** (a 20 MB blob in a repo on a 100 %-full disk). The build
   script, its measured output size and the binary's sha256 are committed; the artefact lives
   at `dist-native/grantforge.exe`.

## 6. Risks, named before they bite

| risk | what it looks like | mitigation |
| --- | --- | --- |
| disk 2.9 GB | Nuitka temp + MinGW download fails midway | budget 1.5 GB; delete `dist-native/` temp after build; report the exact failure if it does not fit |
| 4B model quality | plausible-sounding invented criteria | quote requirement; `unjudged` downgrade; rule engine decides the numeric criteria |
| model endpoint moves | `doctor` says "no model" while the server is fine | both list shapes parsed; endpoint from `GRANTFORGE_LLM_URL`; `doctor` prints the URL it tried |
| MCP stdout purity | a stray `print` corrupts the JSON-RPC stream and the client marks the server failed | all diagnostics to stderr; a test asserts stdout is JSON-lines only |
| patched-Nuitka bug | crash report like the one in `src/` | stdlib-only graph, no transformers plugin, onefile first then standalone |

## 7. Lane split (dispatch is a separate step, not this plan)

- **kilo — build/verify:** run the binary on WSL/Kali (POSIX), verify `doctor` against a
  second endpoint, and confirm the MCP handshake from a non-Windows client.
- **opencode — critique:** attack the admissibility rule (can a quote be fabricated? can a
  rule row be wrong?), and propose the interop hardening (streaming, timeouts, model pinning).

## 8. IT SHALL EVOLVE — the rungs, and what counts as an evolution

Adopted from shardex's L0–L4 ladder: a build is not "done", it is *at a stated rung*,
and the rung is enumerable at runtime rather than asserted in a README.

| rung | what may change | where it attaches | what proves it |
| --- | --- | --- | --- |
| L0 declared | nothing; the build reports itself | `grantforge capabilities --json` | rules, tools, codes, verdicts, statuses, seams |
| L1 additive rule | one criterion | a function in `grants.RULES` returning the same row shape | a new row with `pin.kind == "rule"` |
| L2 additive section | one section set | `rfp.sections`, read by `grants.section_index` | `sections` lists it; `draft` refuses it when undeclared |
| L3 additive tool | one MCP/CLI verb | `mcp.TOOLS` + a branch in `call_tool`; a CLI verb | `capabilities.tools` grows; `tools/list` agrees with it |
| L4 additive failure | one named failure | `errors.ERRORS` code + remedy string | a test that provokes the code, and a CLI run that prints `[code]` + `remedy:` |

Rules that keep the ladder honest:

- **An evolution is valid only if `capabilities` changes.** A capability you cannot
  enumerate at runtime is a capability the next session will re-derive — the cost this
  whole tree pays for rules that live in prose.
- **No silent widening.** The version stays `0.1.0` until a rung is actually occupied
  and covered by a test; the number follows the ladder, never the mood.
- **Sections belong to the RFP.** The tool does not carry a hardcoded section list for
  an RFP that will be replaced next cycle. `section_index` reports each declared
  section as `bounded` (a word limit was read), `unbounded` (declared, no readable
  limit) or `unreadable` (a limit exists in a form this build cannot parse) — the third
  state exists so `"300 words"` is not silently treated as no limit.

## 9. IT SHALL EVOLVE TO FIX ANY/ALL ERRORS — the loop, not the intention

Every failure mode this build can name is a code with a remedy, a ledger row and a
test. Today: **7 codes** (`draft_needs_model`, `input_unreadable`, `model_bad_reply`,
`model_truncated`, `model_unreachable`, `seal_mismatch`, `unknown`).

The loop, applied to any error the user reports or the tool hits:

1. **Reproduce it by running.** A code that was predicted but never provoked does not
   count; the test must reach the failure through the public path.
2. **Name it.** Existing code, or a new one in `errors.ERRORS` with a remedy sentence
   an operator can act on without reading source.
3. **Route it.** CLI prints `[code]` + `remedy:`; MCP returns the same object as
   `content` with `isError: true`. One failure, one shape, both surfaces.
4. **Record it.** `~/.grantforge/errors.jsonl` (`GRANTFORGE_ERRLOG` overrides), appended
   by `errors.record`, which never raises — a logging failure must not become the
   failure the user sees.
5. **Add the test.** The rung-L4 proof.
6. **Keep the exit contract.** `0` ok · `1` a finding (review failure, broken chain) ·
   `2` BLIND (the RFP carried no readable criterion) · `3` model unreachable or
   unusable · `4` input unreadable. **A failure never exits 0**, and `2` is not a pass.

## 10. Forensic investigation architecture with a bypass kit — adopted natively

The design is a finding-producing instrument, so it carries the forensic half rather
than decorating a report with the word "verified".

### 10.1 Chain of custody (`src/grantforge_native/case.py`)

- `case init <dir> <rfp> <profile>` hashes **each input as read** (sha256, byte count,
  path) into `case.json`. An RFP edited after the verdict is a different RFP; the case
  can say so instead of comparing against a memory of it.
- Every step appends one link to `custody.jsonl`:
  `{seq, ts, kind, payload_digest, prev, hash}` where `hash = sha256(prev + payload_digest
  + seq + kind + ts)`. `assess --case DIR` and `draft --case DIR` write their result
  into the chain and return the entry hash as `custody`.
- `case verify <dir>` **recomputes** the chain from the stored bytes and fails at the
  first broken link, naming it: sequence gap, `prev` mismatch, or hash mismatch
  ("entry was altered after it was written"). Exit 1 when broken.
- `case init` **refuses to overwrite a live case** — an append-only log that can be
  re-initialised is not append-only.
- **Claim supported:** these bytes, in this order, unaltered since written.
  **Not claimed:** authorship or identity. There is no signature and deliberately no
  key: a key sitting in the user's home directory is a lock with the key taped to it.

### 10.2 Re-checkable verdicts (ELIZA doctrine)

- Every `assess` row carries `pin`: `{kind, criterion, quote, recheck}` where kind is
  `rule` (a deterministic check the operator can re-run), `quote` (a verbatim span of
  the RFP the model cited) or `none` (nothing was judged). A model's verdict without a
  verbatim quote is `unjudged`, never "likely eligible".
- Top-level `status` is ELIZA's ARC vocabulary: `READY` (every criterion decided),
  `GAPS` (decided where it could, named what it could not), `BLIND` (no criterion was
  readable — exit 2). `INCOMPLETE` is intentionally unused; a build either decided or
  named why not.

### 10.3 The bypass kit (`src/grantforge_native/llm.py`)

Named for what it is: routes around an endpoint that answers "not here", without
inventing results.

| obstacle | route taken |
| --- | --- |
| endpoint given as `host`, `host/v1` or with a path | normalise to the API root once, at construction |
| `/models` returns `{data:[…]}` or a bare list | both shapes accepted |
| 5xx / transport failure | bounded retry with backoff; **4xx is not retried** (a wrong request does not become right) |
| reply truncated at the token budget | re-ask once with budget × 3 (`model_truncated`) |
| model names a different base | `probe` reports base, root, model and reachability; `doctor` prints it |

Scope, stated so it is not over-claimed: it bypasses **address and protocol shape**,
not authentication, and it acquires no evidence from the network. GrantForge reads the
files it is given and the local model it is pointed at.

### 10.4 What is deliberately absent

- No web fetching, no scraping, no crawling: an assessment about an applicant is built
  from the RFP and the profile, and a tool that quietly adds sources cannot be audited
  by the person holding the case file.
- No signature, no key management, no "trusted timestamp" service.
- No automatic rewriting of a draft to "fix" a finding: `review` reports, the operator
  decides. A tool that edits its own evidence is the failure mode forensics exists to
  prevent.

## 11. Evolution harnesses and pushes the agent

The evolution ladder in §8 answers "what may be added". This section answers the
harder question: **how does the agent that drives GrantForge end up properly
harnessed, rather than merely equipped?**

**A tool catalogue is not a harness.** Handing a model nine tools tells it what
exists; it does not tell it which call comes first, what ends a step, or what to do
when a code comes back. So the operating contract is shipped as *data*, generated from
the running build's own tables:

```
grantforge harness --json           # CLI
grantforge_harness                  # MCP tool, any client
```

Both return the same object:

| field | source | why it cannot drift |
| --- | --- | --- |
| `sequence` | `harness.push_sequence()` | each step names a tool that must exist in `mcp.TOOLS` (tested) |
| `on_error` | `errors.ERRORS` + `errors.NEXT` | a code without a next action fails a test |
| `exit_codes` | the CLI contract | asserted as a set `{0,1,2,3,4}` |
| `rules` / `tools` | `grants.RULES`, `mcp.TOOLS` | same objects the binary dispatches through |
| `custody` | `case.py` | the verbs printed are the verbs that exist |

### 11.1 The push is a sequence with stopping conditions

An agent is harnessed when it knows *when to stop*, so every step carries `when`,
`stop_if` and `return_evidence`:

| # | call | stops the run when |
| --- | --- | --- |
| 1 | `grantforge_doctor` | `ok: false` — report `[model_unreachable]` + remedy, do not judge with a dead model |
| 2 | `grantforge_capabilities` | never — this is what prevents re-deriving the build |
| 3 | `grantforge_sections` | the requested section is not declared — do not invent a section set |
| 4 | `grantforge_assess` | `status` is `BLIND` (exit 2) — say so; `GAPS` continues only by naming what stayed unjudged |
| 5 | `grantforge_draft` | the draft reports `unsupported` spans — report, never silently rewrite |
| 6 | `grantforge_review` | `ok: false` — return the findings verbatim |
| 7 | `grantforge_verify` | a recomputed digest disagrees with a seal |

### 11.2 From errors to harness — the loop that closes

`errors.NEXT` is the bridge. Each code carries the action an agent should take next,
in the imperative, naming the command:

| code | next action (abridged) |
| --- | --- |
| `model_unreachable` | run `doctor --json`; start the model; only then `--offline` if rules suffice |
| `model_truncated` | re-run with a larger `max_tokens`, or split the section; never parse truncated text |
| `model_bad_reply` | re-run once; else `--offline` and report `unjudged` — never accept a paraphrase |
| `draft_needs_model` | drop `--offline` for `draft`; a draft is never rules-only |
| `input_unreadable` | re-read the path from the case manifest; never edit the case to match the input |
| `seal_mismatch` | compare recomputed digest, re-run the producer, never rewrite the seal |
| `unknown` | capture `doctor --json` + the exact command, then add a code with remedy **and a test** |

The `unknown` row is the evolution mechanism itself: an unclassified failure is not an
edge case to tolerate, it is the next entry in the taxonomy. That is how "fix any/all
errors" stays a loop instead of a slogan — the taxonomy grows by observed failure, and
each growth is a test that provokes it.

### 11.3 What the push deliberately does not do

- It does not *decide* anything for the agent: it states order, stopping conditions and
  recovery, and leaves judgement to the caller.
- It does not claim the agent followed it. Compliance is evidenced by the artefacts
  (`pin`, `status`, `custody`), not by the harness's presence.
- It does not hide its own gaps: `ledger.last_write_error` is in the contract, so an
  agent can see when the diagnostics ledger itself is not being written.

## 12. Live therapy — the button, not the score

An assessment tells an operator what is true and a review tells them what is wrong.
Neither tells them what to *do first*, and that translation is the step that gets
skipped under deadline. So it becomes one call:

```
grantforge therapy <rfp.json> <profile.json> [--proposal draft.json] [--offline]
grantforge_therapy{rfp, profile, proposal?}          # same thing over MCP
```

**Live** in the sense that matters: both halves re-run now — `assess` against the
RFP/profile in hand, `review` against the draft if one is given — and the plan is
built from *those* readings, never from a stored plan or a previous session's verdict.

### 12.1 What comes back, per defect

| field | meaning |
| --- | --- |
| `code` | the defect's own vocabulary (`MISSING_SECTION`, `unjudged`, `ineligible`, `BLIND`, …) |
| `where` | the section or criterion that owns it — so the fix has an address |
| `severity` | `error` before `warn`; the sort is the treatment order |
| `cause` | why the check fired, in the check's own terms |
| `prescription` | the action, deterministic and keyed by `code` |
| `evidence_needed` | what the prescription has to produce to count |
| `recheck` | the exact command that clears or confirms the finding |

`recheck` is the part that makes therapy falsifiable. The plan is not a mood: run the
prescription, run the recheck, and the finding either clears or it does not. A test
asserts every `recheck` names a verb this build actually registers (`cli.verbs()`), so
a prescription cannot point at a command that does not exist.

### 12.2 Prognosis, and its exit codes

| prognosis | meaning | exit |
| --- | --- | --- |
| `HEALTHY` | nothing to treat | 0 |
| `TREATABLE` | a plan was produced, ordered error-first | 1 |
| `BLIND` | nothing in the RFP could be read at all | 2 |

Exit 1 is deliberate: "a plan exists" is not success, and a caller that pipelines therapy
into a submission step should see a non-zero until the plan is empty. `BLIND` stays
distinct from `TREATABLE` because "cannot read the question" and "the answer needs work"
are different problems with different owners (build vs applicant).

### 12.3 Why the model is not asked to prescribe

Prescriptions come from `therapy.TREATMENTS` / `therapy.STATUS_TREATMENTS`, keyed by the
finding's code. The model's job is unchanged from everywhere else in this build: decide
a criterion *inside `assess`*, and only when its answer quotes the RFP verbatim. A model
that invents a prescription is a second opinion dressed as an instruction — it would read
authoritatively and be unauditable, which is the exact failure mode §11.2 exists to
prevent. So an unregistered review code cannot be silently skipped either: it comes back
as a finding whose prescription is "add an entry to `therapy.TREATMENTS`", which is the
module reporting its own gap rather than hiding it.

### 12.4 Measured, this build (2026-11-05)

| item | reading |
| --- | --- |
| tests | `pytest tests/test_grantforge_native.py` → **71 passed in 9.31s** (`PYTEST_EXIT=0`) |
| binary | `build_grantforge_native.py --json` → ok true, **9,978,632 bytes**, sha256 `c0d60b992ded2098…` |
| MCP tools | 9 (`grantforge_harness`, `grantforge_therapy` added to the 7) |
| CLI verbs | 14, of which `therapy` and `harness` are new |
| live therapy, `BIN-1` fixture | `prognosis TREATABLE`, `status GAPS`, `engine rules+llm`, 1 finding `unjudged @ fit`, **exit 1** |
| custody | `therapy --case` → `custody c8ee36d9…`, then `case verify` → `chain True, entries 2` |
| missing case | `--case <absent>` → **exit 4**, `grantforge: no case at … - run: grantforge case init …` |
| ledger damage | `errors --json` → `unreadable_lines 0` over 17 recorded entries (counted, not swallowed) |
