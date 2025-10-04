# scripts/profile_lint.py
from __future__ import annotations
import json, re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROFILE_PATH = BASE / "profile" / "profile.json"

def warn(msg): print("⚠︎", msg)
def ok(msg): print("✓", msg)

def main():
    if not PROFILE_PATH.exists():
        print("profile/profile.json not found.")
        return
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    # Contact
    c = profile.get("contact", {})
    missing = [k for k in ("location","email","phone","linkedin") if not c.get(k)]
    if missing:
        warn(f"Contact missing: {', '.join(missing)}")
    else:
        ok("Contact block complete.")

    # Experience sanity
    exp = profile.get("experience", [])
    if not exp:
        warn("No experience entries.")
    else:
        ok(f"{len(exp)} experience entries found.")
        for r in exp:
            company = r.get("company","").strip()
            title = r.get("title","").strip()
            dates = r.get("dates","").strip()
            bullets = r.get("bullets", []) or []
            if not company or not title or not dates:
                warn(f"Role missing fields: {company} | {title} | {dates}")
            if not bullets:
                warn(f"{company} — {title}: 0 bullets")
            # Basic bullet quality checks
            long = [b for b in bullets if len(b) > 300]
            no_period = [b for b in bullets if not str(b).strip().endswith(".")]
            if long:
                warn(f"{company} — {title}: {len(long)} very long bullet(s) (>300 chars).")
            if no_period:
                warn(f"{company} — {title}: {len(no_period)} bullet(s) do not end with a period.")

    # Skills presence (unfiltered; filtering happens at build-time)
    for k in ("domains","methods","platforms","security_terms"):
        items = profile.get(k, [])
        if not items:
            warn(f"No values in {k}.")
        else:
            ok(f"{k}: {len(items)} item(s).")

if __name__ == "__main__":
    main()
