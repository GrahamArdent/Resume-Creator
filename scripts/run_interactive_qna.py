from __future__ import annotations
from pathlib import Path
import json, sys, datetime
from utils import slugify, prompt_hash, rewrite_bullet, dedupe_list
from scripts.prompt_engine import generate_questions
from scripts.build_resume import build_pair

BASE = Path(__file__).resolve().parents[1]
JD_PATH = BASE / "data" / "job_posting.txt"
ANSWERS_PATH = BASE / "profile" / "answers.json"
PROFILE_PATH = BASE / "profile" / "profile.json"

def _load_answers() -> dict:
    if ANSWERS_PATH.exists(): data = json.loads(ANSWERS_PATH.read_text(encoding="utf-8"))
    else: data = {}
    data.setdefault("global", {"extra_keywords": [], "summary_additions": []})
    data.setdefault("roles", {}); data.setdefault("asked", {})
    return data

def _save_answers(data: dict) -> None:
    g = data.get("global", {})
    g["extra_keywords"] = dedupe_list([x.strip() for x in g.get("extra_keywords", []) if x and x.strip()])
    g["summary_additions"] = dedupe_list([x.strip() for x in g.get("summary_additions", []) if x and x.strip()])
    for rk, r in data.get("roles", {}).items():
        r["extra_bullets"] = dedupe_list([x.strip() for x in r.get("extra_bullets", []) if x and x.strip()])
    ANSWERS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _prompt_multiline(prompt: str) -> str:
    print(prompt + "\n(Type END on its own line to finish.)")
    lines = []
    while True:
        line = input()
        if line.strip() == "END": break
        lines.append(line)
    return "\n".join(lines).strip()

def main():
    (BASE / "data").mkdir(exist_ok=True)

    print("\n=== Paste job posting ===")
    jd_text = _prompt_multiline("Job description:")
    if not jd_text: print("No description provided."); sys.exit(1)
    JD_PATH.write_text(jd_text, encoding="utf-8")

    company = input("\nCompany name (e.g., WinMagic): ").strip() or "Generic"
    company_slug = slugify(company)
    print(f"Using company slug: {company_slug}")

    style_choice = input("\nPrimary style [1=Balanced, 2=Executive, 3=ATS, 4=Human]: ").strip()
    style = {"1":"balanced","2":"executive","3":"ats","4":"human"}.get(style_choice, "balanced")

    try:
        profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Could not read profile.json: {e}"); sys.exit(1)

    answers = _load_answers()

    print("\nGenerating focused questions (only if relevant)…")
    existing = {"asked_prompts": [k for k in answers.get("asked", {}).keys()]}
    questions = generate_questions(jd_text, existing)

    if questions:
        print("\n=== Answer the following (only NEW items will be saved) ===")
        global_kw = answers.get("global", {}).get("extra_keywords", [])
        for q in questions:
            pid = q["id"]
            if pid in answers["asked"]: continue
            print("\n" + q["prompt"])
            resp = input("> ").strip()
            if not resp: continue
            rewritten = rewrite_bullet(resp, is_current=False, inject_kw=global_kw)
            answers["asked"][pid] = {"prompt": q["prompt"], "answer": rewritten, "type":"freeform", "company_used": company_slug, "timestamp": datetime.datetime.utcnow().isoformat() + "Z"}
            answers["global"].setdefault("summary_additions", []).append(rewritten)

    _save_answers(answers)

    print("\nBuilding primary resume + CV…")
    result = build_pair(primary_style=style, company_slug=company_slug, jd_text=jd_text)

    print("\nGenerated (primary):")
    for k,v in result["primary"].items(): print(f"- {k}: {v}")
    print("\nGenerated (cv):")
    for k,v in result["cv"].items(): print(f"- {k}: {v}")

if __name__ == "__main__":
    main()
