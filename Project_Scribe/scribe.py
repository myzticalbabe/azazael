"""
Project Scribe — Agent form-filler for grant applications.

Uses Playwright for browser automation with stealth capabilities.
Same browser bypass approach as BCC re-investigation (curl_cffi headers + stealth).

Architecture:
  scribe.py          — Main CLI: load profile, target URL, fill & submit
  programs/          — Grant program definitions (URLs, selectors, flow)
  profiles/          — Project profiles (SHARDEX, Nurse Ratchet, etc.)
  sessions/          — Persistent browser sessions with cookies
  evidence/          — Screenshots, network logs, submission receipts

Usage:
  python scribe.py --program epic_megagrants --profile profiles/shardex_profile.json
  python scribe.py --program nlnet --profile profiles/nurse_ratchet_profile.json --dry-run
  python scribe.py --list-programs
"""

import json, os, re, sys, time, argparse, asyncio, random
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print("playwright not installed. pip install playwright && playwright install chromium")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
PROFILES_DIR = BASE_DIR / "profiles"
SESSIONS_DIR = BASE_DIR / "sessions"
EVIDENCE_DIR = BASE_DIR / "evidence"
LOGS_DIR = BASE_DIR / "logs"

for d in (PROFILES_DIR, SESSIONS_DIR, EVIDENCE_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Grant Program Registry ──────────────────────────────────────────────

@dataclass
class GrantProgram:
    key: str
    name: str
    url: str
    description: str
    fields: Dict[str, str]           # profile_key -> CSS selector
    required_docs: List[str]         # file keys from profile
    bypass_config: Dict[str, Any]    # cloudflare, recaptcha, etc.
    submit_selector: str
    success_indicators: List[str]
    dry_run_supported: bool = True
    form_available: bool = True      # whether a web form exists
    application_method: str = "web_form"  # "web_form", "github_issue", "email", "manual"
    # Inclusive numeric bounds the funder states in prose but the HTML does not
    # enforce with min/max. A value outside them is rejected server-side, which
    # reads back as an unlabelled failure, so check it before submitting.
    bounds: Dict[str, Any] = field(default_factory=dict)

PROGRAMS: Dict[str, GrantProgram] = {
    "epic_megagrants": GrantProgram(
        key="epic_megagrants",
        name="Epic MegaGrants",
        url="https://www.unrealengine.com/megagrants",
        description="Epic Games funding for Unreal Engine projects + open-source 3D tools",
        fields={
            "project_name": "input[name='projectName'], input#projectName, [data-testid='project-name']",
            "project_description": "textarea[name='projectDescription'], textarea#projectDescription, [data-testid='project-description']",
            "project_url": "input[name='projectUrl'], input#projectUrl",
            "github_url": "input[name='githubUrl'], input#githubUrl",
            "team_size": "input[name='teamSize'], input#teamSize",
            "funding_amount": "input[name='fundingAmount'], input#fundingAmount",
            "contact_email": "input[name='contactEmail'], input#contactEmail",
            "contact_name": "input[name='contactName'], input#contactName",
        },
        required_docs=["pitch_deck", "prototype_video", "github_repo"],
        bypass_config={"cloudflare": True, "recaptcha": "v2"},
        submit_selector="button[type='submit'], button[data-testid='submit-application'], input[type='submit']",
        success_indicators=["application submitted", "confirmation", "thank you", "received"],
        form_available=False,
        application_method="manual",
    ),
    "nlnet": GrantProgram(
        key="nlnet",
        name="NLnet Foundation",
        url="https://nlnet.nl/propose/",
        description="Open source internet infrastructure, developer tools, security",
        fields={
            "call": "select[name='call']",
            "project": "input[name='project']",
            "website": "input[name='website']",
            "website2": "input[name='website2']",
            "website3": "input[name='website3']",
            "website4": "input[name='website4']",
            "abstract": "textarea[name='abstract']",
            "amount": "input[name='amount']",
            "use": "textarea[name='use']",
            "comparison": "textarea[name='comparison']",
            "challenges": "textarea[name='challenges']",
            "ecosystem": "textarea[name='ecosystem']",
            "experience": "textarea[name='experience']",
            "otherfunding": "textarea[name='otherfunding']",
            "requestor": "input[name='requestor']",
            "email": "input[name='email']",
            "pgp": "textarea[name='pgp']",
            "phone": "input[name='phone']",
            "entity": "select[name='entity']",
            "organization": "input[name='organization']",
            "country": "select[name='country']",
            "used_ai": "select[name='used_ai']",
            "codebase_used_ai": "select[name='codebase_used_ai']",
        },
        required_docs=["proposal", "budget", "timeline"],
        bypass_config={"cloudflare": False},
        submit_selector="input[type='submit']",
        success_indicators=["submitted", "thank you", "reference number", "received", "success"],
        bounds={"amount": (5000, 50000)},
    ),
    "github_secure_oss": GrantProgram(
        key="github_secure_oss",
        name="GitHub Secure Open Source Fund",
        url="https://github.com/securitylab/secure-open-source-fund",
        description="Security tooling grants for open source projects (apply via GitHub Issues)",
        fields={
            "repo_url": "input[name='repository_url'], input#repository_url",
            "project_description": "textarea[name='description'], textarea#description",
            "security_focus": "textarea[name='security_focus'], textarea#security_focus",
            "maintainer_github": "input[name='maintainer'], input#maintainer",
            "contact_email": "input[name='email'], input#email",
        },
        required_docs=["security_audit", "threat_model"],
        bypass_config={"cloudflare": False, "github_auth": True},
        submit_selector="button[type='submit']",
        success_indicators=["submitted", "application received", "received"],
        form_available=False,
        application_method="github_issue",
    ),
    "herodevs": GrantProgram(
        key="herodevs",
        name="HeroDevs OSS Sustainability Fund",
        url="https://herodevs.com/oss-fund",
        description="Maintainers of end-of-life open source developer tools (page returns 404)",
        fields={
            "project_name": "input[name='project'], input#project",
            "package_manager": "select[name='package_manager'], select#package_manager",
            "version_maintained": "input[name='version'], input#version",
            "maintainer_since": "input[name='since'], input#since",
            "contact_email": "input[name='email'], input#email",
        },
        required_docs=["adoption_metrics", "maintenance_plan"],
        bypass_config={"cloudflare": True},
        submit_selector="button[type='submit'], input[type='submit']",
        success_indicators=["application received", "thank you", "received"],
        form_available=False,
        application_method="manual",
    ),
    "nlnet_open_call": GrantProgram(
        key="nlnet_open_call",
        name="NLnet Open Call (NGI)",
        url="https://nlnet.nl/propose/",
        description="NGI open call for internet infrastructure, privacy, search (same form as NLnet)",
        fields={
            "call": "select[name='call']",
            "project": "input[name='project']",
            "website": "input[name='website']",
            "website2": "input[name='website2']",
            "website3": "input[name='website3']",
            "website4": "input[name='website4']",
            "abstract": "textarea[name='abstract']",
            "amount": "input[name='amount']",
            "use": "textarea[name='use']",
            "comparison": "textarea[name='comparison']",
            "challenges": "textarea[name='challenges']",
            "ecosystem": "textarea[name='ecosystem']",
            "experience": "textarea[name='experience']",
            "otherfunding": "textarea[name='otherfunding']",
            "requestor": "input[name='requestor']",
            "email": "input[name='email']",
            "pgp": "textarea[name='pgp']",
            "phone": "input[name='phone']",
            "entity": "select[name='entity']",
            "organization": "input[name='organization']",
            "country": "select[name='country']",
            "used_ai": "select[name='used_ai']",
            "codebase_used_ai": "select[name='codebase_used_ai']",
        },
        required_docs=["proposal", "budget_breakdown", "milestones"],
        bypass_config={"cloudflare": False},
        submit_selector="input[type='submit']",
        success_indicators=["submitted", "thank you", "reference number", "received", "success"],
        form_available=True,
        application_method="web_form",
        bounds={"amount": (5000, 50000)},
    ),
}

# ── Profile Schema ──────────────────────────────────────────────────────

@dataclass
class ProjectProfile:
    project_name: str
    project_description: str
    project_url: str
    github_url: str
    team_size: int
    funding_amount: str
    contact_name: str
    contact_email: str
    license: str = "CDDL-1.1"
    pitch_deck: str = ""
    prototype_video: str = ""
    github_repo: str = ""
    proposal: str = ""
    budget: str = ""
    timeline: str = ""
    security_audit: str = ""
    threat_model: str = ""
    adoption_metrics: str = ""
    maintenance_plan: str = ""
    budget_breakdown: str = ""
    milestones: str = ""
    overrides: Dict[str, Dict[str, str]] = field(default_factory=dict)
    # Keys a profile file carries that this dataclass does not name. They used
    # to be dropped by from_dict(), which silently discarded exactly the
    # fields the NLnet form asks for (project, amount, requestor, email, pgp,
    # website2-4, otherfunding) and left the form blank.
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        out = {k: v for k, v in self.__dict__.items() if k != "extra"}
        out.update(self.extra)
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectProfile":
        known: Dict[str, Any] = {}
        extra: Dict[str, Any] = {}
        for k, v in data.items():
            (known if k in cls.__annotations__ else extra)[k] = v
        known["extra"] = extra
        return cls(**known)

    def get_field(self, key: str, program_key: str = "") -> str:
        """Resolve a form field name to a value.

        Order: per-program override, verbatim profile key (known or extra), then
        the FIELD_ALIASES bridge, because profiles say project_name/contact_email
        while forms say project/email.
        """
        if program_key and program_key in self.overrides and key in self.overrides[program_key]:
            return self.overrides[program_key][key]
        for candidate in [key] + FIELD_ALIASES.get(key, []):
            for holder in (getattr(self, candidate, ""), self.extra.get(candidate, "")):
                if holder not in ("", None) and not isinstance(holder, (dict, list)):
                    return str(holder)
        return ""


# Profile vocabulary -> form vocabulary. A field name a form uses that is not
# in a profile still resolves here, so renaming a form field cannot make an
# application arrive empty.
FIELD_ALIASES: Dict[str, List[str]] = {
    "project": ["project_name"],
    "website": ["project_url", "github_url", "github_repo"],
    "requestor": ["contact_name"],
    "email": ["contact_email"],
    "amount": ["funding_amount"],
    "abstract": ["project_description"],
}

# Input types that are never fillable from a profile string.
UNFILLABLE_TYPES = {"submit", "button", "file", "hidden", "checkbox", "radio", "reset", "image"}


def parse_form_schema(html: str) -> Dict[str, Dict[str, Any]]:
    """Read the live form's own field list: name, tag, type, required, maxlength.

    The page is the schema. PROGRAMS[...].fields is a hint that can drift the
    moment a funder renames an input; this cannot.
    """
    schema: Dict[str, Dict[str, Any]] = {}

    def attrs(blob: str) -> Dict[str, str]:
        return {k.lower(): v for k, v in re.findall(r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*"([^"]*)"', blob)}

    def maxlen(a: Dict[str, str]) -> int:
        raw = a.get("maxlength", "")
        return int(raw) if raw.isdigit() else 0

    for m in re.finditer(r"<input([^>]*)>", html, re.I):
        a = attrs(m.group(1))
        name = a.get("name", "").strip()
        if not name:
            continue
        schema[name] = {"tag": "input", "type": a.get("type", "text").lower(),
                        "required": "required" in a, "maxlength": maxlen(a), "options": []}

    for m in re.finditer(r"<select([^>]*)>(.*?)</select>", html, re.I | re.S):
        a = attrs(m.group(1))
        name = a.get("name", "").strip()
        if not name:
            continue
        schema[name] = {"tag": "select", "type": "select", "required": "required" in a,
                        "maxlength": 0,
                        "options": [o for o in re.findall(r'<option[^>]*value="([^"]*)"', m.group(2)) if o]}

    for m in re.finditer(r"<textarea([^>]*)>", html, re.I):
        a = attrs(m.group(1))
        name = a.get("name", "").strip()
        if not name:
            continue
        schema[name] = {"tag": "textarea", "type": "textarea", "required": "required" in a,
                        "maxlength": maxlen(a), "options": []}

    return schema


def audit_submission(schema: Dict[str, Dict[str, Any]], values: Dict[str, str],
                     bounds: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """What the page itself would reject. A required-empty field is a stop, not a retry."""
    missing = [n for n, m in schema.items()
               if m["required"] and m["type"] not in UNFILLABLE_TYPES
               and not str(values.get(n, "")).strip()]
    overflow = [n for n, v in values.items()
                if schema.get(n, {}).get("maxlength") and len(str(v)) > schema[n]["maxlength"]]
    out_of_bounds = []
    for name, (low, high) in (bounds or {}).items():
        raw = str(values.get(name, "")).strip().replace(",", "").replace("$", "").replace("\u20ac", "")
        if not raw:
            continue
        try:
            number = float(raw)
        except ValueError:
            out_of_bounds.append(f"{name}={raw!r} is not numeric")
            continue
        if not low <= number <= high:
            out_of_bounds.append(f"{name}={number:g} outside [{low:g}, {high:g}]")
    return {"ok": not missing and not overflow and not out_of_bounds,
            "missing_required": missing,
            "overflow": overflow,
            "out_of_bounds": out_of_bounds,
            "filled": sorted(values),
            "field_count": len(schema)}


def load_page_feedback(program_key: str) -> Optional[Dict[str, Any]]:
    """The previous run's own verdict, so the next run starts from it."""
    path = EVIDENCE_DIR / f"{program_key}_page_feedback.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        print(f"  [WARN] page feedback unreadable at {path}: {exc!r}; "
              f"starting with no prior verdict")
        return None

# ── Stealth Browser Session ─────────────────────────────────────────────

STEALTH_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-CH-UA": '"Chromium";v="120", "Not_A Brand";v="8"',
    "Sec-CH-UA-Mobile": "?0",
    "Sec-CH-UA-Platform": '"Windows"',
}

class ScribeSession:
    def __init__(self, program: GrantProgram, session_id: str = None):
        self.program = program
        self.session_id = session_id or f"scribe_{int(time.time())}"
        self.session_file = SESSIONS_DIR / f"{self.session_id}.json"
        self.evidence_dir = EVIDENCE_DIR / f"{self.program.key}_{self.session_id}"
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.schema: Dict[str, Dict[str, Any]] = {}
        self.attempted: Dict[str, str] = {}

    async def start(self, headless: bool = True):
        self.playwright = await async_playwright().start()
        
        # Launch with stealth args
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        )

        # Create context with stealth settings
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers=STEALTH_HEADERS,
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
        )

        # Add stealth scripts
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        # Load session cookies
        if self.session_file.exists():
            cookies = json.loads(self.session_file.read_text())
            await self.context.add_cookies(cookies)

        self.page = await self.context.new_page()

    async def goto(self, url: str, wait_for: str = "networkidle") -> Page:
        """Navigate to URL with Cloudflare handling."""
        response = await self.page.goto(url, wait_until=wait_for, timeout=60000)

        # Check for Cloudflare challenge
        if response and response.status in (403, 503):
            await self._handle_cloudflare_challenge()

        # Random human-like delay
        await asyncio.sleep(random.uniform(1.0, 2.5))
        return self.page

    async def _handle_cloudflare_challenge(self):
        """Wait for Cloudflare challenge to complete."""
        print("  [CF] Cloudflare challenge detected, waiting...")
        try:
            # Wait for challenge to complete (max 120s)
            await self.page.wait_for_load_state("networkidle", timeout=120000)
            # Check if we're past the challenge
            content = await self.page.content()
            if "challenge" in content.lower() or "cf-browser-verification" in content.lower():
                # Still in challenge, wait more
                await asyncio.sleep(5)
                await self.page.wait_for_load_state("networkidle", timeout=60000)
        except Exception as exc:
            print(f"  [WARN] cloudflare wait did not settle: {exc!r}")
        await self._save_cookies()

    async def fill_form(self, profile: ProjectProfile) -> bool:
        """Fill every field the LIVE page declares.

        The page is the schema, not PROGRAMS[...]['fields']: a form that renamed
        an input must not receive a blank submission. Long values are set in one
        go --- typing 4000 chars at 50-150ms costs ~7 minutes per field and was
        another reason these runs never finished.
        """
        if not self.page:
            return False

        self.schema = parse_form_schema(await self.page.content())
        self.attempted = {}
        print(f"  [PAGE] {len(self.schema)} named fields on the live form")

        for name, meta in self.schema.items():
            if meta["type"] in UNFILLABLE_TYPES:
                continue
            value = profile.get_field(name, self.program.key)
            if not value:
                continue

            limit = meta.get("maxlength") or 0
            if limit and len(value) > limit:
                print(f"  [TRUNC] {name}: {len(value)} -> {limit} chars (page maxlength)")
                value = value[:limit]

            selector = f"{meta['tag']}[name='{name}']"
            try:
                if meta["tag"] == "select":
                    await self.page.select_option(selector, value=value)
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                elif len(value) > 200:
                    await self.page.fill(selector, value)
                else:
                    element = await self.page.wait_for_selector(selector, timeout=5000)
                    await element.click()
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    await element.fill("")
                    for char in value:
                        await element.type(char, delay=random.uniform(20, 60))
                    await asyncio.sleep(random.uniform(0.2, 0.5))
                self.attempted[name] = value
                print(f"  [FILL] {name} <- {value[:50]!r}")
            except Exception as exc:
                print(f"  [WARN] {name}: {type(exc).__name__} (value resolved, fill failed)")

        return True

    async def audit(self) -> Dict[str, Any]:
        """Re-read the live form after filling and report what submit would reject."""
        if not self.page:
            return {"ok": False, "missing_required": ["<no page>"], "overflow": [],
                    "filled": [], "field_count": 0}
        self.schema = parse_form_schema(await self.page.content())
        result = audit_submission(self.schema, self.attempted, self.program.bounds)
        result["program"] = self.program.key
        result["checked_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        return result

    def save_page_feedback(self, audit: Dict[str, Any]) -> Path:
        """Persist this run's page verdict where the next run will read it."""
        path = EVIDENCE_DIR / f"{self.program.key}_page_feedback.json"
        path.write_text(json.dumps(audit, indent=2))
        print(f"  [ADAPT] wrote {path}")
        return path

    async def upload_files(self, profile: ProjectProfile) -> bool:
        """Upload required documents - stub for now."""
        # File uploads are highly site-specific
        # Would need per-program implementation
        print(f"  [UPLOAD] Document upload not yet implemented for {self.program.key}")
        return True

    async def submit(self) -> bool:
        """Click submit and verify success."""
        if not self.page:
            return False

        try:
            # Try each submit selector
            selectors = [s.strip() for s in self.program.submit_selector.split(",")]
            submitted = False

            for selector in selectors:
                try:
                    btn = await self.page.wait_for_selector(selector, timeout=5000)
                    if btn:
                        await btn.click()
                        await self.page.wait_for_load_state("networkidle", timeout=30000)
                        submitted = True
                        print(f"  [SUBMIT] Clicked submit button")
                        break
                except Exception as exc:
                    print(f"  [WARN] submit selector {selector!r} failed: {exc!r}")
                    continue

            if not submitted:
                print(f"  [ERROR] No submit button found")
                return False

            # Check for success indicators
            await asyncio.sleep(2)
            content = await self.page.content()
            content_lower = content.lower()

            for indicator in self.program.success_indicators:
                if indicator.lower() in content_lower:
                    print(f"  [OK] Success indicator found: {indicator}")
                    await self._save_cookies()
                    await self._save_evidence("success")
                    return True

            print(f"  [WARN] No success indicator found. Content preview: {content[:500]}")
            await self._save_evidence("uncertain")
            return False

        except Exception as e:
            print(f"  [ERROR] Submit failed: {e}")
            await self._save_evidence("error")
            return False

    async def _save_cookies(self):
        if self.context:
            cookies = await self.context.cookies()
            self.session_file.write_text(json.dumps(cookies, indent=2))

    async def _save_evidence(self, stage: str):
        """Save screenshot and page content for audit."""
        if not self.page:
            return

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # Screenshot
        screenshot_path = self.evidence_dir / f"{stage}_{timestamp}.png"
        await self.page.screenshot(path=str(screenshot_path), full_page=True)

        # Page content
        content_path = self.evidence_dir / f"{stage}_{timestamp}.html"
        content = await self.page.content()
        content_path.write_text(content, encoding="utf-8")

        print(f"  [EVIDENCE] Saved to {self.evidence_dir}")

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# ── Main Application ────────────────────────────────────────────────────

class ScribeApp:
    def __init__(self):
        self.profile: Optional[ProjectProfile] = None
        self.program: Optional[GrantProgram] = None

    def load_profile(self, path: str) -> ProjectProfile:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Profile not found: {path}")
        data = json.loads(p.read_text())
        self.profile = ProjectProfile.from_dict(data)
        return self.profile

    def create_profile_template(self, path: str):
        template = ProjectProfile(
            project_name="My Project",
            project_description="Brief description of the project",
            project_url="https://github.com/user/project",
            github_url="https://github.com/user/project",
            team_size=1,
            funding_amount="$25,000",
            contact_name="Your Name",
            contact_email="you@example.com",
        )
        Path(path).write_text(json.dumps(template.to_dict(), indent=2))
        print(f"Created template at {path}")

    def list_programs(self):
        print("\nAvailable Grant Programs:")
        print("-" * 60)
        for key, prog in PROGRAMS.items():
            print(f"  {key:25} — {prog.name}")
            print(f"  {'':25}   {prog.description}")
            print(f"  {'':25}   URL: {prog.url}")
            print()

    async def apply(self, program_key: str, profile_path: str, headless: bool = True,
                    dry_run: bool = False) -> bool:
        if program_key not in PROGRAMS:
            raise ValueError(f"Unknown program: {program_key}. Available: {list(PROGRAMS.keys())}")

        self.program = PROGRAMS[program_key]
        self.load_profile(profile_path)

        print(f"\n{'='*60}")
        print(f"SCRIBE — Grant Application Agent")
        print(f"Program: {self.program.name}")
        print(f"Profile: {self.profile.project_name}")
        print(f"Method: {self.program.application_method}")
        print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print(f"{'='*60}\n")

        # For programs without web forms, generate filled application document
        if not self.program.form_available:
            return await self._generate_application_doc(dry_run)

        session = ScribeSession(self.program)

        try:
            await session.start(headless=headless)
            await session.goto(self.program.url)

            print(f"[NAV] Loaded {self.program.url}")

            # Start from the last run's own verdict instead of rediscovering it.
            prior = load_page_feedback(self.program.key)
            if prior and prior.get("missing_required"):
                print(f"[ADAPT] previous run ({prior.get('checked_at', '?')}) was blocked on "
                      f"{len(prior['missing_required'])} unfilled required field(s):")
                for name in prior["missing_required"][:12]:
                    print(f"        - {name}")

            # Fill form
            print(f"[FILL] Filling form fields...")
            await session.fill_form(self.profile)

            # Upload documents
            print(f"[UPLOAD] Checking document uploads...")
            await session.upload_files(self.profile)

            # Ask the page whether it would accept this, before pretending to submit.
            audit = await session.audit()
            session.save_page_feedback(audit)
            print(f"[AUDIT] {audit['field_count']} fields | filled {len(audit['filled'])} | "
                  f"missing_required {len(audit['missing_required'])} | "
                  f"overflow {len(audit['overflow'])} | out_of_bounds {len(audit['out_of_bounds'])}")
            if audit["missing_required"]:
                print("[AUDIT] required but empty: " + ", ".join(audit["missing_required"]))
            if audit["overflow"]:
                print("[AUDIT] over page maxlength: " + ", ".join(audit["overflow"]))
            if audit["out_of_bounds"]:
                print("[AUDIT] outside funder bounds: " + ", ".join(audit["out_of_bounds"]))

            # The page has already said what it will reject. Adapt instead of
            # clicking submit and reading `uncertain` back a 33rd time. This runs
            # in dry-run too, so a dry run that would be rejected is not "OK".
            hard_blockers = audit["missing_required"] + audit["overflow"] + audit["out_of_bounds"]
            if hard_blockers:
                print(f"\n[BLOCKED] Not submitting: {len(hard_blockers)} problem(s) the page names.")
                for name in audit["missing_required"]:
                    print(f"          empty required field: {name}")
                for name in audit["overflow"]:
                    print(f"          exceeds page maxlength: {name}")
                for name in audit["out_of_bounds"]:
                    print(f"          outside funder range: {name}")
                await session._save_evidence("blocked_required_fields")
                return False

            if dry_run:
                print(f"\n[DRY RUN] Form would be accepted. Stopping before actual submission.")
                await session._save_evidence("dry_run_ready")
                return True

            # Submit
            print(f"[SUBMIT] Submitting application...")
            success = await session.submit()

            if success:
                print(f"\n[SUCCESS] Application submitted to {self.program.name}!")
            else:
                print(f"\n[FAILURE] Submission may have failed. Check evidence in {session.evidence_dir}")

            return success

        finally:
            await session.close()

    async def _generate_application_doc(self, dry_run: bool) -> bool:
        """Generate a filled application document for manual submission."""
        print(f"[DOC] Generating application document for {self.program.application_method} submission...")
        
        # Build filled application data
        app_data = {
            "program": self.program.name,
            "program_key": self.program.key,
            "url": self.program.url,
            "method": self.program.application_method,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "profile": self.profile.project_name,
            "fields": {}
        }
        
        # Fill in all fields from profile
        for field_key in self.program.fields:
            value = self.profile.get_field(field_key, self.program.key)
            if value:
                app_data["fields"][field_key] = value
        
        # Add overrides
        if self.program.key in self.profile.overrides:
            for field_key, value in self.profile.overrides[self.program.key].items():
                if value:
                    app_data["fields"][field_key] = value
        
        # Save application document
        output_dir = EVIDENCE_DIR / f"{self.program.key}_application_{int(time.time())}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON
        json_path = output_dir / f"application_{self.program.key}.json"
        json_path.write_text(json.dumps(app_data, indent=2))
        
        # Save human-readable markdown
        md_path = output_dir / f"application_{self.program.key}.md"
        md_lines = [
            f"# {self.program.name} Application",
            f"",
            f"**Program:** {self.program.name}",
            f"**URL:** {self.program.url}",
            f"**Method:** {self.program.application_method}",
            f"**Generated:** {app_data['generated_at']}",
            f"**Profile:** {app_data['profile']}",
            f"",
            f"## Filled Fields",
            f"",
        ]
        for field_key, value in app_data["fields"].items():
            md_lines.append(f"### {field_key}")
            md_lines.append(f"")
            md_lines.append(f"```")
            md_lines.append(f"{value}")
            md_lines.append(f"```")
            md_lines.append(f"")
        
        md_path.write_text("\n".join(md_lines))
        
        print(f"\n[DOC] Application document generated:")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")
        print(f"  Directory: {output_dir}")
        
        if dry_run:
            print(f"\n[DRY RUN] Document generated. Ready for manual submission via {self.program.application_method}.")
            return True
        
        print(f"\n[READY] Application document ready for manual submission.")
        print(f"Submit via: {self.program.application_method}")
        return True

async def dry_run_all(profile_path: str, headless: bool = True) -> int:
    """Dry-run every registered program, streaming one live log.

    Nothing is submitted. Each program's outcome is classified OK / BLOCKED /
    ERROR so the next pass knows what to fix; the exit code is non-zero if any
    program ERRORed, because a run that could not be performed is not a pass.
    """
    log_path = LOGS_DIR / f"scribe_dryrun_{time.strftime('%Y%m%d_%H%M%S')}.log"
    log_file = open(log_path, "w", encoding="utf-8", errors="replace")
    original_stdout = sys.stdout

    class _Tee:
        def write(self, s):
            original_stdout.write(s)
            log_file.write(s)
            log_file.flush()
            return len(s)

        def flush(self):
            original_stdout.flush()
            log_file.flush()

    sys.stdout = _Tee()
    results: Dict[str, Dict[str, Any]] = {}
    try:
        print(f"\n{'#'*66}")
        print(f"# DRY RUN ALL — {len(PROGRAMS)} programs, profile {Path(profile_path).name}")
        print(f"# log: {log_path}")
        print(f"# nothing will be submitted")
        print(f"{'#'*66}", flush=True)

        app = ScribeApp()
        for key, program in PROGRAMS.items():
            print(f"\n=== {key} | {program.application_method} | {program.url}", flush=True)
            started = time.time()
            try:
                ok = await app.apply(key, profile_path, headless=headless, dry_run=True)
                state = "OK" if ok else "BLOCKED"
                detail = ""
            except Exception as exc:
                state = "ERROR"
                detail = f"{type(exc).__name__}: {exc}"
                print(f"[TRACE] {detail}", flush=True)
            elapsed = time.time() - started
            results[key] = {"state": state, "detail": detail, "seconds": round(elapsed, 1),
                            "method": program.application_method}
            print(f"--- {key}: {state} in {elapsed:.1f}s {detail}", flush=True)

        print(f"\n{'='*66}")
        print(f"{'PROGRAM':24s} {'METHOD':13s} {'STATE':9s} SEC")
        print(f"{'-'*66}")
        for key, r in results.items():
            print(f"{key:24s} {r['method']:13s} {r['state']:9s} {r['seconds']}")
        errors = [k for k, r in results.items() if r["state"] == "ERROR"]
        blocked = [k for k, r in results.items() if r["state"] == "BLOCKED"]
        clean = [k for k, r in results.items() if r["state"] == "OK"]
        print(f"{'-'*66}")
        print(f"{len(clean)} ok | {len(blocked)} blocked | {len(errors)} error")
        if blocked:
            print("blocked on empty required fields: " + ", ".join(blocked))
        if errors:
            print("errored: " + ", ".join(errors))
        print(f"log: {log_path}")
        return 1 if errors else 0
    finally:
        sys.stdout = original_stdout
        log_file.close()


async def main():
    parser = argparse.ArgumentParser(
        prog="scribe",
        description="Project Scribe — Agent form-filler for grant applications"
    )
    parser.add_argument("--program", help="Grant program key (use --list to see all)")
    parser.add_argument("--profile", help="Path to project profile JSON")
    parser.add_argument("--list", action="store_true", help="List available programs")
    parser.add_argument("--create-profile", help="Create a template profile at PATH")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser headless")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run browser visible")
    parser.add_argument("--dry-run", action="store_true", help="Fill form but don't submit")
    parser.add_argument("--dry-run-all", action="store_true",
                        help="Dry-run every registered program into one live log (submits nothing)")

    args = parser.parse_args()

    app = ScribeApp()

    if args.list:
        app.list_programs()
        return 0

    if args.create_profile:
        app.create_profile_template(args.create_profile)
        return 0

    if args.dry_run_all:
        if not args.profile:
            parser.error("--dry-run-all requires --profile")
        return await dry_run_all(args.profile, headless=args.headless)

    if not args.program or not args.profile:
        parser.print_help()
        return 1

    success = await app.apply(args.program, args.profile, headless=args.headless, dry_run=args.dry_run)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))