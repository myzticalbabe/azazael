"""Tests for chain_server.py -- the endpoint a user points their own model at.

The properties that matter are refusals, not features:

* no model configured -> 503 with a reason (never an echoed prompt);
* no usable frame -> 422 and NO `aio` field (never a short answer a client can use);
* a model's text is NEVER stored as verified -- only /verify with the acceptance
  command's own exit code can do that;
* a failed verification writes a lesson, which is the loop that was empty until now.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
TOOLS = HERE / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import chain_server as cs  # noqa: E402  (path set above, deliberately)
import memory_bridge as bridge  # noqa: E402


@pytest.fixture()
def state(tmp_path: Path) -> str:
    return str(tmp_path)


@pytest.fixture()
def server(state: str):
    httpd = cs.make_server(port=0, state_dir=state)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:%d" % httpd.server_address[1]
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture()
def model_server():
    """A stand-in for Ollama/llama.cpp: the OpenAI chat shape and nothing else."""

    class Stub(BaseHTTPRequestHandler):
        calls: list = []

        def log_message(self, *args):  # silence
            pass

        def do_POST(self):  # noqa: N802
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            Stub.calls.append(body)
            out = json.dumps({"choices": [{"message": {"content": "STUB ANSWER"}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Stub)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:%d/v1" % httpd.server_address[1], Stub
    httpd.shutdown()
    httpd.server_close()


def post(base: str, path: str, payload: dict):
    request = urllib.request.Request(
        base + path, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def get(base: str, path: str):
    with urllib.request.urlopen(base + path, timeout=20) as response:
        return response.status, json.loads(response.read())


GOOD = {
    "prompt": "refuse a shard whose golden run does not reproduce",
    "target": "tools/sword.py",
    "acceptance": "pytest -q exits 0 and prints 98 passed",
    "evidence": "tests/test_defender.py",
    "defends": ["the golden run's state_sha256 token"],
    "must_not_break": ["tests/test_defender.py"],
    "control": "flip one byte in state_sha256 and require a REFUSAL",
    "root": str(HERE),
}


# --------------------------------------------------------------------------- #
# Health, and the absence it reports
# --------------------------------------------------------------------------- #

def test_health_says_there_is_no_model(server: str) -> None:
    status, body = get(server, "/health")
    assert status == 200
    assert body["model"] is False
    assert body["shape"] == "defensive-aio-v1"


def test_ask_without_a_model_is_503_not_an_echo(server: str) -> None:
    status, body = post(server, "/ask", GOOD)
    assert status == 503
    assert body["state"] == "NO-MODEL"
    assert "does not have a model" in body["reason"] or "no --model-url" in body["reason"]
    assert "answer" not in body


# --------------------------------------------------------------------------- #
# The frame and the sentinel, in front of every answer
# --------------------------------------------------------------------------- #

def test_aio_returns_an_instruction_object_and_writes_the_frame(server: str,
                                                               state: str) -> None:
    status, body = post(server, "/aio", GOOD)
    assert status == 200, body
    assert "AIO  defensive-aio-v1" in body["aio"]
    assert body["frame_id"].startswith("f-")
    frames = Path(state) / bridge.FRAMES_FILE
    assert frames.exists()
    assert body["frame_id"] in frames.read_text(encoding="utf-8")


def test_a_prompt_with_no_finish_line_is_422_and_carries_no_prompt(server: str) -> None:
    status, body = post(server, "/aio", {**GOOD, "acceptance": ""})
    assert status == 422
    assert "aio" not in body
    assert body["problems"]


def test_a_ghost_target_is_blocked_by_the_sentinel(server: str) -> None:
    status, body = post(server, "/aio", {**GOOD, "target": "tools/ghost.py"})
    assert status == 422
    assert any("sentinel" in problem for problem in body["problems"])


# --------------------------------------------------------------------------- #
# The model: a transport, never an authority
# --------------------------------------------------------------------------- #

def test_ask_reaches_a_stub_model_and_never_claims_verified(model_server, state: str) -> None:
    url, stub = model_server
    httpd = cs.make_server(port=0, state_dir=state, model_url=url, model_name="stub")
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:%d" % httpd.server_address[1]
    try:
        status, body = post(base, "/ask", GOOD)
    finally:
        httpd.shutdown()
        httpd.server_close()
    assert status == 200, body
    assert body["answer"] == "STUB ANSWER"
    assert body["verified"] is False
    assert stub.calls and stub.calls[0]["temperature"] == 0
    system = stub.calls[0]["messages"][0]
    assert system["role"] == "system" and "AIO  defensive-aio-v1" in system["content"]


# --------------------------------------------------------------------------- #
# Verification, and the lesson it writes
# --------------------------------------------------------------------------- #

def test_verify_records_success_without_a_lesson(server: str, state: str) -> None:
    status, body = post(server, "/verify", {"frame_id": "f-abc", "command": "pytest -q",
                                            "exit_code": 0})
    assert status == 200
    assert body["verdict"] == "VERIFIED"
    assert body["lesson"] == "not needed"
    assert not (Path(state) / bridge.LESSONS_FILE).exists()


def test_verify_records_failure_and_writes_a_recallable_lesson(server: str,
                                                              state: str) -> None:
    status, body = post(server, "/verify", {"frame_id": "f-abc", "command": "pytest -q",
                                            "exit_code": 1,
                                            "observed": "2 failed, 96 passed"})
    assert status == 200
    assert body["verdict"] == "FAILED"
    assert body["lesson"] == "written"
    found = bridge.recall("acceptance command exited", jsonl=str(
        Path(state) / bridge.LESSONS_FILE))
    assert found["state"] == bridge.MEMORY
    assert found["matches"], "the failed verification is not recallable"


def test_verify_refuses_without_a_frame_or_command(server: str) -> None:
    status, body = post(server, "/verify", {"frame_id": ""})
    assert status == 422
    assert body["problems"]


# --------------------------------------------------------------------------- #
# The loop the user did not know was empty
# --------------------------------------------------------------------------- #

def test_the_lesson_ledger_is_written_by_the_chain_itself(state: str) -> None:
    """Before this, nothing wrote lessons.jsonl, so every run was UNMEMORED."""
    written = bridge.record_lesson(
        "a golden run that does not reproduce must be refused, not rebaselined",
        kind="lesson", trigger="verify", state_dir=state)
    assert Path(written["path"]).exists()
    again = bridge.record_lesson(
        "a golden run that does not reproduce must be refused, not rebaselined",
        state_dir=state)
    assert again["skipped"] == "duplicate"
    found = bridge.recall("golden run reproduce", jsonl=written["path"])
    assert found["state"] == bridge.MEMORY and found["matches"]


def test_a_lesson_too_short_to_decide_anything_is_refused(state: str) -> None:
    with pytest.raises(ValueError):
        bridge.record_lesson("it broke", state_dir=state)
