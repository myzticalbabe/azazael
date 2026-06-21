#!/usr/bin/env python3
"""xref_webhook.py — utility functions (notify_new_links)""",
"""Webhook notifier for new cross-reference links."""


__all__ = [
    "notify_new_links",
]

import json
import urllib.request
import urllib.error
# from typing import Optional  # removed — all names have native equivalents

def notify_new_links(new_links: int, total: int, webhook_url: str) -> bool:
    payload = json.dumps({
        "text": f"🔗 New cross-reference links created: +{new_links} (total: {total})",
        "new_links": new_links,
        "total_mappings": total,
    }).encode()
    try:
        req = urllib.request.Request(webhook_url, data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=5)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else input("Webhook URL: ")
    test = notify_new_links(5, 100, url)
    print(f"Notification {'sent' if test else 'failed'}")
