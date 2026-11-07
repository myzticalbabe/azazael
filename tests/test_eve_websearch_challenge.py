"""Tests for the challenge ladder: detection names the wall, the ladder
climbs, and a surviving challenge reads `blocked` -- never empty, never
invented. One live test renders a real page headless."""
from eve_unleashed import websearch as _w


def test_detect_cloudflare_iuam():
    body = ("<html><head><title>Just a moment...</title></head><body>"
            "<form id='cf-chl'>checking your browser</form></body></html>")
    assert _w.detect_challenge(403, {}, body) == "cloudflare-iuam"


def test_detect_turnstile():
    body = ('<div class="cf-turnstile" data-sitekey="x"></div>'
            '<script src="https://challenges.cloudflare.com/turnstile/v0/api.js">')
    assert _w.detect_challenge(200, {}, body) == "cloudflare-iuam"


def test_detect_cf_ray_403():
    assert _w.detect_challenge(403, {"Server": "cloudflare",
                                     "CF-RAY": "abc123"}, "<html>deny</html>"
                             ) == "cloudflare-deny"


def test_detect_imperva_incapsula():
    body = ("<html><body><script>var z='visid_incap_123';</script>"
            "<iframe src='/._incap_/res/'>Request unsuccessful. "
            "Incapsula incident ID</iframe></body></html>")
    assert _w.detect_challenge(403, {"X-Iinfo": "1-2-3"}, body) == \
        "imperva"


def test_clean_page_is_none():
    body = "<html><body><h1>Example Domain</h1></body></html>"
    assert _w.detect_challenge(200, {}, body) is None


def test_bare_403_is_not_challenge():
    assert _w.detect_challenge(403, {}, "<html>forbidden</html>") is None


def test_fetch_plain_page_ok_first_rung():
    res = _w.fetch_visible("https://example.com")
    assert res["state"] == "ok", res
    assert res["rung"] == "plain"
    assert "Example Domain" in res["text"]


def test_fetch_empty_url_rejected():
    import pytest
    with pytest.raises(ValueError):
        _w.fetch_visible("   ")


def test_live_headless_render_executes():
    text, err = _w._render_fetch("https://example.com")
    assert err is None, err
    assert "documentation examples" in text
