#!/usr/bin/env python3
"""Build a send-safe RTK/FIU outbox and receipt ledger.

This tool automates queueing, validation, send-ready rendering, and receipt
logging. It never transmits anything: external RTK/FOIA/FIU sends and filings
are human-executed only.

Typical use:
    python azazael/scripts/rtk_fiu_outbox.py --build
    python azazael/scripts/rtk_fiu_outbox.py --build --write-outbox \
        --outbox-path research/bcc_analysis/rtkl_requests/outbox.json
    python azazael/scripts/rtk_fiu_outbox.py --render-ready \
        --sender-profile /path/to/sender_profile.json
    python azazael/scripts/rtk_fiu_outbox.py --record-receipt \
        --item 18 --channel email --sent-at 2026-11-19T12:00:00Z \
        --confirmation AGENCY-123 --outbox-path ... --receipts-path ...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LETTERS_DIR = REPO_ROOT / "research" / "bcc_analysis" / "rtkl_requests"
DEFAULT_INDEX = DEFAULT_LETTERS_DIR / "rtkl_requests_index.json"
REQUIRED_PLACEHOLDERS = ("[Requester Name]", "[Address]", "[Email]", "[Phone]")
RECEIPT_CHANNELS = ("email", "portal", "mail", "in-person", "phone", "other")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("missing JSON file: %s" % path, file=sys.stderr)
        return None
    except json.JSONDecodeError as exc:
        raise SystemExit("invalid JSON in %s: %s" % (path, exc))


def build_outbox(letters_dir: Path, index_path: Path, extra_items_path=None):
    if not letters_dir.is_dir():
        raise SystemExit("letters directory not found: %s" % letters_dir)
    index = load_json(index_path)
    if index is None:
        raise SystemExit("request index not found: %s" % index_path)

    items = []
    errors = []
    requests = index.get("requests", {})
    for key in sorted(requests, key=str):
        entry = requests[key]
        filename = entry.get("filename", "")
        letter_path = letters_dir / filename
        if not letter_path.is_file():
            errors.append("missing letter file for item %s: %s" % (key, filename))
            continue
        text = letter_path.read_text(encoding="utf-8", errors="replace")
        placeholders = [p for p in REQUIRED_PLACEHOLDERS if p in text]
        items.append(
            {
                "id": str(key),
                "kind": "RTK",
                "agency": entry.get("agency", ""),
                "subject": entry.get("subject", ""),
                "records_count": entry.get("records_count", 0),
                "source_file": str(letter_path.relative_to(REPO_ROOT)),
                "sha256": sha256_file(letter_path),
                "bytes": letter_path.stat().st_size,
                "placeholders_found": placeholders,
                "status": "DRAFT-UNSENT",
                "send_action": "human sends the rendered request to the agency Open Records Officer",
            }
        )

    if extra_items_path:
        extra_path = Path(extra_items_path)
        extra = load_json(extra_path)
        if extra is None:
            raise SystemExit("extra items file not found: %s" % extra_path)
        if not isinstance(extra, list):
            raise SystemExit("extra items file must contain a JSON list")
        for row in extra:
            items.append(
                {
                    "id": str(row.get("id", "")),
                    "kind": str(row.get("kind", "MANUAL")),
                    "agency": str(row.get("agency", "")),
                    "subject": str(row.get("subject", "")),
                    "records_count": int(row.get("records_count", 0)),
                    "source_file": str(row.get("source_file", "")),
                    "sha256": str(row.get("sha256", "")),
                    "bytes": int(row.get("bytes", 0)),
                    "placeholders_found": list(row.get("placeholders_found", [])),
                    "status": "DRAFT-UNSENT",
                    "send_action": str(
                        row.get("send_action", "human executes this send")
                    ),
                }
            )

    return {
        "generated_at": utcnow(),
        "letters_dir": str(letters_dir.relative_to(REPO_ROOT)),
        "index": str(index_path.relative_to(REPO_ROOT)),
        "item_count": len(items),
        "items": items,
        "errors": errors,
    }


def load_sender_profile(path: Path):
    profile = load_json(path)
    if profile is None:
        raise SystemExit("sender profile not found: %s" % path)
    required = ("requester_name", "address", "email", "phone", "human_sender_ack")
    missing = [k for k in required if not profile.get(k)]
    if missing:
        raise SystemExit("sender profile missing: %s" % ", ".join(missing))
    if profile.get("human_sender_ack") is not True:
        raise SystemExit("sender profile must set human_sender_ack to true")
    return profile


def render_ready(outbox, profile, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered = []
    for item in outbox["items"]:
        if item.get("kind") != "RTK":
            continue
        source = REPO_ROOT / item["source_file"]
        text = source.read_text(encoding="utf-8", errors="replace")
        text = text.replace("[Requester Name]", profile["requester_name"])
        text = text.replace("[Address]", profile["address"])
        text = text.replace("[Email]", profile["email"])
        text = text.replace("[Phone]", profile["phone"])
        target = output_dir / ("READY_%s.txt" % Path(source).name)
        target.write_text(text, encoding="utf-8")
        item["status"] = "READY-TO-SEND"
        item["rendered_file"] = str(target.relative_to(REPO_ROOT))
        item["rendered_sha256"] = sha256_file(target)
        rendered.append(item["id"])
    outbox["rendered_at"] = utcnow()
    outbox["rendered_count"] = len(rendered)
    return outbox


def record_receipt(outbox_path, receipts_path, item, channel, sent_at, confirmation, note=""):
    outbox = load_json(Path(outbox_path))
    if outbox is None:
        raise SystemExit("outbox not found: %s" % outbox_path)
    ids = {row.get("id") for row in outbox.get("items", [])}
    if item not in ids:
        raise SystemExit("unknown outbox item: %s" % item)
    if channel not in RECEIPT_CHANNELS:
        raise SystemExit("invalid channel: %s" % channel)
    receipt = {
        "recorded_at": utcnow(),
        "item": item,
        "channel": channel,
        "sent_at": sent_at,
        "confirmation": confirmation,
        "note": note,
        "status": "SENT-BY-HUMAN",
    }
    path = Path(receipts_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(receipt) + "\n")
    return receipt


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--letters-dir", default=str(DEFAULT_LETTERS_DIR))
    parser.add_argument("--index-path", default=str(DEFAULT_INDEX))
    parser.add_argument("--extra-items")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--write-outbox", action="store_true")
    parser.add_argument("--outbox-path", default="")
    parser.add_argument("--render-ready", action="store_true")
    parser.add_argument("--sender-profile", default="")
    parser.add_argument("--ready-dir", default="")
    parser.add_argument("--record-receipt", action="store_true")
    parser.add_argument("--item", default="")
    parser.add_argument("--channel", default="", choices=RECEIPT_CHANNELS)
    parser.add_argument("--sent-at", default="")
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--note", default="")
    parser.add_argument("--receipts-path", default="")
    parser.add_argument("--transmit-all", action="store_true")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.transmit_all:
        print(
            "REFUSED: this tool does not transmit RTK/FIU requests. "
            "External sends are human-executed only; use --build, "
            "--render-ready, and --record-receipt.",
            file=sys.stderr,
        )
        return 2

    letters_dir = Path(args.letters_dir)
    index_path = Path(args.index_path)
    outbox = build_outbox(letters_dir, index_path, args.extra_items or None)

    if args.render_ready:
        if not args.sender_profile:
            raise SystemExit("--render-ready requires --sender-profile")
        profile = load_sender_profile(Path(args.sender_profile))
        ready_dir = (
            Path(args.ready_dir)
            if args.ready_dir
            else letters_dir / "ready_to_send"
        )
        outbox = render_ready(outbox, profile, ready_dir)

    if args.record_receipt:
        for flag in ("item", "channel", "sent_at", "confirmation"):
            if not getattr(args, flag):
                raise SystemExit("--record-receipt requires --%s" % flag.replace("_", "-"))
        if not args.outbox_path or not args.receipts_path:
            raise SystemExit("--record-receipt requires --outbox-path and --receipts-path")
        receipt = record_receipt(
            args.outbox_path,
            args.receipts_path,
            args.item,
            args.channel,
            args.sent_at,
            args.confirmation,
            args.note,
        )
        print(json.dumps(receipt, indent=2))
        return 0

    if args.write_outbox:
        if not args.outbox_path:
            raise SystemExit("--write-outbox requires --outbox-path")
        target = Path(args.outbox_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(outbox, indent=2), encoding="utf-8")
        print("wrote %s (%d items)" % (target, outbox["item_count"]))
        return 0

    print(json.dumps(outbox, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
