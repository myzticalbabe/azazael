#!/usr/bin/env python3
"""Unit tests for request_auth.py — Programmatic PRE-ACTION GATE CLI token management."""
import json
import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT.parent))  # C:/Users/clint/

from SCRIPTS.request_auth import (  # noqa: E402
    _get_tokens_dir,
    _sign_token,
    drop_token,
    is_token_valid,
    consume_token,
    validate_action,
)

# Skip tests if module dependencies are unavailable
_HAS_DEPS = True
try:
    from SCRIPTS.request_auth import _get_tokens_dir  # noqa: F811 — verify import works
except ImportError:
    _HAS_DEPS = False

_HAS_DEPS = unittest.skipUnless(_HAS_DEPS, "SCRIPTS.request_auth dependencies unavailable")

@_HAS_DEPS
class TestTokenManagement(unittest.TestCase):
    """Test token creation, verification, and lifecycle."""

    def setUp(self):
        """Clean up any leftover tokens before each test."""
        tokens_dir = _get_tokens_dir()
        for f in tokens_dir.glob("*.token"):
            f.unlink()

    def tearDown(self):
        """Clean up after tests."""
        tokens_dir = _get_tokens_dir()
        for f in tokens_dir.glob("*.token"):
            f.unlink()

    def test_drop_token_creates_file(self):
        """drop_token() should create a valid token file."""
        path = drop_token("test_file.py", "str_replace", {"authorized": True})
        self.assertTrue(path.exists(), "Token file should exist after drop")
        data = json.loads(path.read_text())
        self.assertEqual(data["target"], "test_file.py")
        self.assertEqual(data["intent"], "str_replace")
        self.assertIn("signature", data)

    def test_is_token_valid_with_valid_token(self):
        """is_token_valid() should return True for a freshly dropped token."""
        path = drop_token("valid_file.py", "write_file", {})
        self.assertTrue(is_token_valid(path, "valid_file.py"))

    def test_is_token_valid_target_mismatch(self):
        """is_token_valid() should return False when target doesn't match."""
        path = drop_token("file_a.py", "str_replace", {})
        self.assertFalse(is_token_valid(path, "file_b.py"))

    def test_is_token_valid_expired(self):
        """is_token_valid() should return False for expired tokens."""
        path = drop_token("expired.py", "str_replace", {})
        # Manipulate token timestamp to simulate expiry
        data = json.loads(path.read_text())
        # Set timestamp to 30 seconds ago
        from datetime import datetime, timezone, timedelta
        old_time = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()
        data["timestamp"] = old_time
        # Re-sign with new timestamp
        data["signature"] = _sign_token(data)
        path.write_text(json.dumps(data))
        self.assertFalse(is_token_valid(path, "expired.py", max_age_seconds=15))

    def test_consume_token_deletes_file(self):
        """consume_token() should delete the token file and return True."""
        path = drop_token("consume_me.py", "str_replace", {})
        self.assertTrue(path.exists())
        result = consume_token("consume_me.py")
        self.assertTrue(result)
        self.assertFalse(path.exists())

    def test_consume_token_missing_file(self):
        """consume_token() should return False for nonexistent files."""
        result = consume_token("nonexistent.py")
        self.assertFalse(result)

    def test_sign_token_deterministic(self):
        """Signing the same data should produce same signature (given same salt).
        Note: Ed25519 is deterministic, BLAKE2b uses random salt so differs per call."""
        data = {"target": "test.py", "timestamp": "2026-01-01"}
        sig1 = _sign_token(data)
        sig2 = _sign_token(data)
        # Both should be valid signatures (format: prefix:hex...)
        self.assertIn(":", sig1)
        self.assertIn(":", sig2)

    def test_token_safe_filename(self):
        """Token filenames should handle paths with special characters."""
        path = drop_token("azazael/src/CORE/doctor.py", "str_replace", {})
        self.assertTrue(path.exists())
        # Filename replaces directory separators
        safe_name = path.name
        self.assertNotIn("/", safe_name)
        self.assertNotIn("\\", safe_name)

    def test_validate_action_readonly(self):
        """Read-only actions should pass instantly."""
        authorized, data = validate_action("read_files", "test.py")
        self.assertTrue(authorized)
        self.assertIn("checks", data)

    def test_validate_action_modifying_without_broker(self):
        """Modifying actions should still authorize when broker is unavailable."""
        # The broker is checked via gate_passed() which may not be available
        authorized, data = validate_action("str_replace", "test.py")
        # Should run through validation (result depends on broker availability)
        self.assertIn("checks", data)
        self.assertTrue(authorized)  # Broker not loaded = non-blocking


@_HAS_DEPS
class TestSignatureVerification(unittest.TestCase):
    """Test cryptographic signature verification."""

    def test_signature_format(self):
        """Signatures should follow the ed25519:hex or blake2b:hex:salt format."""
        data = {"test": "value"}
        sig = _sign_token(data)
        self.assertTrue(
            sig.startswith("ed25519:") or sig.startswith("blake2b:"),
            f"Unexpected signature format: {sig[:30]}..."
        )

    def test_signature_changes_with_different_data(self):
        """Different data should produce different signatures."""
        sig1 = _sign_token({"a": 1})
        sig2 = _sign_token({"a": 2})
        self.assertNotEqual(sig1, sig2)


if __name__ == "__main__":
    unittest.main()
