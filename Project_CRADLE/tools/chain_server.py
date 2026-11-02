# coding: utf-8
"""chain_server -- one local endpoint a user can point their own model at.

WHAT THIS FIXES
---------------
Everything in this project until now was a prompter for an agent that already exists:
kilo, opencode, a coding assistant someone else installed. An end user with their own
model -- Ollama, llama.cpp, vLLM, LM Studio, anything OpenAI-compatible -- had no way in.
The chain produced a prompt and then stopped, so "plug and play" was a claim about
documentation rather than about the code.

This is the missing surface, and it is deliberately the smallest one that is true:

    python tools/chain_server.py --model-url http://127.0.0.1:11434/v1 \\
        --model-name llama3.1 --port 8770

    POST /aio     {prompt, target, acceptance, evidence, defends, must_not_break}
                  -> 200 {frame_id, aio}      the instruction object
                  -> 422 {state, problems}    refused, and NO prompt is returned
    POST /ask     the same fields, plus the model call
                  -> 200 {frame_id, answer, model}
                  -> 503 {state: "NO-MODEL", reason}   when none is configured
    POST /verify  {frame_id, command, exit_code, observed}
                  -> 200 {verdict: "VERIFIED"|"FAILED"}; a FAILED writes a lesson
    GET  /health  -> {ok, model, state_dir, frames, lessons}
    GET  /frames  -> the last 20 frames, newest last

DESIGN RULES, EACH BOUGHT BY A FAILURE
--------------------------------------
* **No model, no answer.** Without --model-url, /ask answers 503 with a reason. It does
  not echo the prompt back, summarise it, or pretend. The estate's whole thesis is that
  an absence reported as a result is the expensive defect; a server is no exception.
* **No frame, no prompt.** /aio and /ask run the frame and the sentinel first. A refusal
  is returned as 422 with the problems, and the `aio` field is absent -- a client cannot
  mistake a refusal for a short answer.
* **The model is a transport, never an authority.** /ask returns the model's text
  unmodified and says `verified: false`. Only /verify, with the acceptance command's own
  exit code, can mark a frame verified. A model's opinion that it worked is not evidence,
  and this server will not store it as any.
* **Stdlib only.** urllib for the model call, http.server for the endpoint. A user who
  has Python has the server; there is nothing to pip install, nothing to compile.

SECURITY, STATED PLAINLY
------------------------
It binds 127.0.0.1 by default and has NO authentication: it is a local tool for one
operator, and binding it to 0.0.0.0 would publish an endpoint that runs commands on
request. --host exists because someone will need it; the help text says what it costs.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def _sibling(name: str):
    import importlib.util

    path = HERE / ("%s.py" % name)
    spec = importlib.util.spec_from_file_location("flaming_sword_%s" % name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


defender = _sibling("defender")
bridge = _sibling("memory_bridge")

SHAPE = "defensive-aio-v1"
DEFAULT_PORT = 8770
MODEL_TIMEOUT = 120


class ModelUnavailable(Exception):
    """No model configured, or it did not answer. Never a fabricated completion."""


# --------------------------------------------------------------------------- #
# The model: OpenAI-compatible, because that is what every local runtime speaks
# --------------------------------------------------------------------------- #

def ask_model(aio: str, prompt: str, model_url: str, model_name: str,
              api_key: str = "", timeout: int = MODEL_TIMEOUT) -> str:
    """POST the AIO as the system instruction and return the text, unmodified."""
    if not model_url:
        raise ModelUnavailable("no --model-url configured; the chain does not have a "
                              "model of its own and will not invent one")
    url = model_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model_name or "local",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": aio},
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    if api_key:
        request.add_header("Authorization", "Bearer %s" % api_key)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        raise ModelUnavailable("%s returned HTTP %d: %s"
                               % (url, exc.code, exc.read()[:200].decode(
                                   "utf-8", errors="replace"))) from exc
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise ModelUnavailable("%s did not answer: %s" % (url, exc)) from exc
    try:
        return str(payload["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise ModelUnavailable("the model answered in an unexpected shape: %s"
                               % json.dumps(payload)[:200]) from exc


# --------------------------------------------------------------------------- #
# The chain, as functions (the HTTP layer is a thin shell over these)
# --------------------------------------------------------------------------- #

def aio_for(payload: Dict[str, Any], state_dir: Optional[str]) -> Tuple[int, Dict[str, Any]]:
    """(status, body). 200 carries an AIO; 422 carries the refusal and no prompt."""
    prompt = str(payload.get("prompt") or payload.get("intent") or "").strip()
    if not prompt:
        return 422, {"state": "REFUSED", "problems": ["no prompt was supplied"]}
    lessons = bridge.recall(prompt, jsonl=str(Path(state_dir) / bridge.LESSONS_FILE)
                            if state_dir else None)
    result = defender.to_aio(
        prompt,
        target=str(payload.get("target") or ""),
        acceptance=str(payload.get("acceptance") or ""),
        evidence=str(payload.get("evidence") or ""),
        defends=payload.get("defends") or [],
        must_not_break=payload.get("must_not_break") or [],
        control=str(payload.get("control") or ""),
        refusal=str(payload.get("refusal") or ""),
        preserve=bool(payload.get("preserve")),
        memory=lessons,
        root=payload.get("root") or None,
    )
    body: Dict[str, Any] = {"state": result["state"],
                            "frame_id": result.get("frame", {}).get("frame_id"),
                            "memory": lessons.get("state"),
                            "problems": result.get("problems") or []}
    if result.get("problems"):
        return 422, body
    body["aio"] = result["aio"]
    written = bridge.record(result["frame"], state_dir=state_dir)
    body["frames"] = written["path"]
    return 200, body


def ask(payload: Dict[str, Any], state_dir: Optional[str], model_url: str,
        model_name: str, api_key: str = "") -> Tuple[int, Dict[str, Any]]:
    status, body = aio_for(payload, state_dir)
    if status != 200:
        return status, body
    try:
        answer = ask_model(body["aio"], str(payload.get("prompt")), model_url,
                           model_name, api_key)
    except ModelUnavailable as exc:
        return 503, {"state": "NO-MODEL", "reason": str(exc),
                     "frame_id": body.get("frame_id")}
    # The instruction that produced this answer, by hash. The sentinel can check a frame;
    # nothing could check WHICH instruction the model was given until this field existed,
    # and an answer is only reproducible if the instruction is nameable.
    import hashlib

    instruction_sha = hashlib.sha256(body["aio"].encode("utf-8")).hexdigest()
    return 200, {"state": "ANSWERED", "frame_id": body.get("frame_id"),
                 "model": model_name or "local", "answer": answer,
                 "instruction_sha256": instruction_sha,
                 "verified": False,
                 "note": "a model's text is not evidence; POST /verify with the "
                         "acceptance command to mark this frame verified. Check the "
                         "instruction with tools/inference_sentinel.py"}


def verify(payload: Dict[str, Any], state_dir: Optional[str]) -> Tuple[int, Dict[str, Any]]:
    frame_id = str(payload.get("frame_id") or "").strip()
    command = str(payload.get("command") or "").strip()
    if not frame_id or not command:
        return 422, {"state": "REFUSED",
                     "problems": ["frame_id and command are both required"]}
    try:
        exit_code = int(payload.get("exit_code", 0))
    except (TypeError, ValueError):
        return 422, {"state": "REFUSED", "problems": ["exit_code must be an integer"]}
    written = bridge.record_verification(frame_id, command, exit_code,
                                         str(payload.get("observed") or ""),
                                         state_dir=state_dir)
    return 200, {"state": written["verdict"], "verdict": written["verdict"],
                 "path": written["path"],
                 "lesson": "written" if written.get("lesson") else "not needed"}


def health(state_dir: Optional[str], model_url: str, model_name: str) -> Dict[str, Any]:
    directory = Path(state_dir) if state_dir else Path.cwd() / bridge.STATE_DAY_DIR
    frames = bridge._read_jsonl(directory / bridge.FRAMES_FILE)[0] \
        if (directory / bridge.FRAMES_FILE).exists() else []
    lessons = bridge._read_jsonl(directory / bridge.LESSONS_FILE)[0] \
        if (directory / bridge.LESSONS_FILE).exists() else []
    return {"ok": True, "shape": SHAPE, "state_dir": str(directory),
            "model": bool(model_url), "model_url": model_url or "",
            "model_name": model_name or "",
            "instruction": "per-frame: the AIO is the system instruction, and /ask "
                           "echoes its sha256 so the instruction is nameable",
            "frames": len(frames), "lessons": len(lessons),
            "refuses": ["no model -> 503", "no frame -> 422",
                        "a model's text is never 'verified'"]}


# --------------------------------------------------------------------------- #
# HTTP shell
# --------------------------------------------------------------------------- #

class Handler(BaseHTTPRequestHandler):
    server_version = "flaming-sword-chain/1"
    config: Dict[str, Any] = {}

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter by default
        if self.config.get("verbose"):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, status: int, body: Dict[str, Any]) -> None:
        raw = json.dumps(body, indent=1, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _payload(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}

    def do_GET(self) -> None:  # noqa: N802 (http.server's spelling)
        cfg = self.config
        if self.path in ("/health", "/"):
            return self._send(200, health(cfg.get("state_dir"), cfg.get("model_url", ""),
                                          cfg.get("model_name", "")))
        if self.path == "/frames":
            directory = Path(cfg.get("state_dir") or
                             Path.cwd() / bridge.STATE_DAY_DIR)
            path = directory / bridge.FRAMES_FILE
            frames, error = bridge._read_jsonl(path) if path.exists() else ([], None)
            return self._send(200, {"frames": frames[-20:], "error": error})
        return self._send(404, {"state": "NOT-FOUND", "path": self.path})

    def do_POST(self) -> None:  # noqa: N802
        cfg = self.config
        payload = self._payload()
        try:
            if self.path == "/aio":
                status, body = aio_for(payload, cfg.get("state_dir"))
            elif self.path == "/ask":
                status, body = ask(payload, cfg.get("state_dir"), cfg.get("model_url", ""),
                                   cfg.get("model_name", ""), cfg.get("api_key", ""))
            elif self.path == "/verify":
                status, body = verify(payload, cfg.get("state_dir"))
            else:
                status, body = 404, {"state": "NOT-FOUND", "path": self.path}
        except Exception as exc:  # the server must answer, not vanish
            status, body = 500, {"state": "ERROR", "reason": "%s: %s"
                                 % (type(exc).__name__, exc)}
        return self._send(status, body)


def make_server(port: int = DEFAULT_PORT, host: str = "127.0.0.1",
                state_dir: Optional[str] = None, model_url: str = "",
                model_name: str = "", api_key: str = "",
                verbose: bool = False) -> ThreadingHTTPServer:
    handler = type("BoundHandler", (Handler,), {
        "config": {"state_dir": state_dir, "model_url": model_url,
                   "model_name": model_name, "api_key": api_key,
                   "verbose": verbose}})
    return ThreadingHTTPServer((host, port), handler)


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="One local endpoint: user prompt -> frame -> sentinel -> AIO, and "
                    "your own model pointed at it.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--host", default="127.0.0.1",
                        help="127.0.0.1 by default. This server has NO authentication "
                             "and runs the acceptance commands it is given: binding it "
                             "to 0.0.0.0 publishes that to the network")
    parser.add_argument("--model-url", default="",
                        help="an OpenAI-compatible base URL, e.g. "
                             "http://127.0.0.1:11434/v1 (Ollama) or "
                             "http://127.0.0.1:8080/v1 (llama.cpp). Empty means no "
                             "model: /ask answers 503 and says so")
    parser.add_argument("--model-name", default="", help="model id your runtime expects")
    parser.add_argument("--api-key", default="", help="only for a remote endpoint")
    parser.add_argument("--state-dir", default=None,
                        help="where frames/lessons/verifications are written "
                             "(default: ./.flaming_sword)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    server = make_server(args.port, args.host, args.state_dir, args.model_url,
                         args.model_name, args.api_key, args.verbose)
    host, port = server.server_address[:2]
    print("chain server on http://%s:%d" % (host, port))
    print("  model: %s" % ((" %s (%s)" % (args.model_name or "local", args.model_url))
                            if args.model_url else
                            "NONE configured -- /ask will answer 503, which is not the "
                            "same as a model that failed"))
    print("  state: %s" % (args.state_dir or str(Path.cwd() / bridge.STATE_DAY_DIR)))
    print("  endpoints: GET /health, GET /frames, POST /aio, POST /ask, POST /verify")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
