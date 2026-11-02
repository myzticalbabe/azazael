# PROJECT CRADLE

The cradle holds the work, and hands it to whatever model you already run.

Four parts that existed and did not know about each other, behind one command:

| part | what it guards | where it lives |
| --- | --- | --- |
| **FLAMING SWORD** | the codebase — find, queue, fix, prove, land | `Project_FLAMING_SWORD/tools/sword.py` |
| **defender** | the user's intent — a prompt becomes a frame that can be satisfied or refused | `Project_FLAMING_SWORD/tools/defender.py` |
| **sentinel** | the frame's claims — every path stat'ed, every act from a closed vocabulary | `Project_FLAMING_SWORD/tools/sentinel.py` |
| **memory** | what was learned — recalled, or reported UNMEMORED with its reason | `Project_FLAMING_SWORD/tools/memory_bridge.py` |

CRADLE adds no judgement of its own. It launches them, in the order that makes each
answer meaningful, and it serves the result to the model the user already has.

## Three commands

```bash
python Project_CRADLE/cradle.py --doctor     # is this machine ready, and what is missing
python Project_CRADLE/cradle.py --demo       # prove the loop end to end, no model needed
python Project_CRADLE/cradle.py --serve --model-url http://127.0.0.1:11434/v1 --model-name llama3.1
```

`--doctor` prints a line per requirement and exits 1 on any failure. It does not say
"looks good": python's version, each part's path, whether the state directory is
writable, whether git exists, and whether your model answers.

`--demo` runs the real tools against a real file in a throwaway directory — and it
includes **a deliberate failed verification**, so you can watch a lesson get written and
then get recalled. A demo that shows only the happy path teaches nothing about what the
gates refuse.

`--serve` starts one local endpoint. Your model stays yours: CRADLE never holds weights,
never needs an API key, and speaks the OpenAI chat shape every local runtime already
implements.

| runtime | `--model-url` | notes |
| --- | --- | --- |
| Ollama | `http://127.0.0.1:11434/v1` | `ollama pull llama3.1 && ollama serve` |
| llama.cpp | `http://127.0.0.1:8080/v1` | `llama-server -m model.gguf` |
| LM Studio | `http://127.0.0.1:1234/v1` | start the local server in the app |
| vLLM | `http://127.0.0.1:8000/v1` | serves an OpenAI-compatible API |

## Endpoints

```
GET  /health     {ok, model: true|false, frames, lessons, what it refuses}
GET  /frames     the last 20 frames
POST /aio        {prompt, target, acceptance, evidence, defends, must_not_break}
                 -> 200 {frame_id, aio}      an instruction object
                 -> 422 {state, problems}    refused, and NO prompt is returned
POST /ask        the same fields; runs the AIO through your model
                 -> 200 {frame_id, answer, verified: false}
                 -> 503 {state: "NO-MODEL", reason}   when none is configured
POST /verify     {frame_id, command, exit_code, observed}
                 -> 200 {verdict: "VERIFIED" | "FAILED"}; a FAILED writes a lesson
```

Three refusals, and each exists because its absence produced a wrong answer once:

- **No model, no answer.** Without `--model-url`, `/ask` returns 503 with the reason. It
  does not echo the prompt, summarise it, or invent a completion.
- **No frame, no prompt.** If the frame or the sentinel refuses, the response is 422 and
  the `aio` field is *absent* — a client cannot mistake a refusal for a short answer.
- **A model's text is never evidence.** `/ask` returns `verified: false` and says so.
  Only `/verify`, carrying the acceptance command's own exit code, can mark a frame
  verified.

## What was hard about receiving this, and what changed

Written after auditing the hand-off as a stranger would meet it. Each finding is
something that was measured in this tree, not guessed:

1. **Doctrine before action.** The README opened with *why* the project exists, and the
   first runnable command printed decision blocks. A newcomer's first question is "what
   do I type", and the answer was four sections down. Now: three commands, at the top of
   this file, with the first one needing no model, no key and no build.
2. **No declared dependency or minimum interpreter.** Measured: no `requirements.txt`,
   no `pyproject.toml`, no `setup.py`. That is correct — the tree is stdlib-only — but a
   stranger assumes a missing manifest means missing install steps, and either runs `pip
   install` at nothing or gives up. Now `--doctor` states the interpreter, and the
   absence of dependencies is a printed PASS rather than an omission.
3. **No single entry point.** Five tools, five invocations, and the order between them
   lived in prose. Now `cradle.py` runs them in the only order that makes each answer
   meaningful, and `--demo` proves the order works.
4. **Model-agnostic, with no adapter.** Measured: `grep` for `openai`, `/v1/chat`,
   `Authorization` across the project returned **nothing**. "Point it at your model" was
   a claim about documentation, not a capability in the code. Now `/ask` is a real
   OpenAI-compatible client, and `/health` says plainly whether a model is configured.
5. **The memory was never written.** This is the one that mattered most and nobody knew:
   the bridge could *read* a lesson ledger and nothing ever *wrote* one, so every run
   reported `UNMEMORED` — honestly, which is exactly why it went unnoticed. The report
   was true and the pipe was empty. Now a failed verification writes a lesson at the
   moment it fails, a duplicate is refused (a ledger where the same lesson appears forty
   times stops being believed), and `--demo` shows the write and the recall in one run.

## What this does not do

- **The sentinel judges a frame, not an inference.** It stats paths; it does not assert
  which model answered, which endpoint, or which instruction hash. If you need that, it
  is a session-start config assertion, and it does not exist here yet.
- **`--serve` has no authentication.** It binds `127.0.0.1` and runs the acceptance
  commands it is given. `--host 0.0.0.0` publishes that to your network; the help text
  says so.
- **A frame is still advisory unless something requires it.** `sword --run` does not yet
  refuse a batch whose queued items have no frame — that is the open half (M-42).

## Uninstall

Delete `Project_CRADLE/` and `Project_FLAMING_SWORD/`, and remove `.flaming_sword/` from
whichever directory you served from. There is no service, no registry entry, no
`site-packages` copy, and nothing outside those paths.
