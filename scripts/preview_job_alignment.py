# scripts/preview_job_alignment.py
from __future__ import annotations
import re, json, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROFILE_PATH = BASE / "profile" / "profile.json"
ANSWERS_PATH = BASE / "profile" / "answers.json"

def extract_keywords(jd_text: str) -> set[str]:
    words = re.findall(r"[A-Za-z0-9\-\+]+", jd_text)
    ignore = {"the","and","with","for","of","to","a","in","on","at","as","by","or"}
    return set(w.lower() for w in words if len(w) > 2 and w.lower() not in ignore)

def _load_txt(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

def main():
    ap = argparse.ArgumentParser(description="Preview JD-driven skill filtering (no writes).")
    ap.add_argument("--jd-file", default=str(BASE / "data" / "job_posting.txt"),
                    help="Path to JD text file (default: data/job_posting.txt)")
    args = ap.parse_args()

    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    answers = json.loads(ANSWERS_PATH.read_text(encoding="utf-8")) if ANSWERS_PATH.exists() else {"global": {}}

    jd_text = _load_txt(Path(args.jd_file))
    if not jd_text.strip():
        print("No JD found. Provide --jd-file or put text in data/job_posting.txt")
        return

    kw = extract_keywords(jd_text)
    kw_lower = set(kw)

    def filter_relevant(items):
        keep, drop = [], []
        for i in items:
            if any(tok in kw_lower for tok in i.lower().split()):
                keep.append(i)
            else:
                drop.append(i)
        return keep, drop

    report = {}
    for label in ("domains","methods","platforms","security_terms"):
        keep, drop = filter_relevant(profile.get(label, []))
        report[label] = {"keep": keep, "drop": drop}

    print("\n=== JD Filter Preview ===")
    print("JD tokens detected:", ", ".join(sorted(kw))[:800] + ("…" if len(",".join(sorted(kw)))>800 else ""))
    for label in ("domains","methods","platforms","security_terms"):
        block = report[label]
        print(f"\n[{label.upper()}]")
        print("  Keep:", ", ".join(block["keep"]) or "(none)")
        print("  Drop:", ", ".join(block["drop"]) or "(none)")

    # Show summary additions that will appear (curated only, no write)
    curated = answers.get("global", {}).get("summary_additions", [])
    if curated:
        print("\n[SUMMARY ADDITIONS (curated)]")
        for i, line in enumerate(curated[:10], 1):
            print(f"  {i}. {line}")
    else:
        print("\n[SUMMARY ADDITIONS] (none)")

if __name__ == "__main__":
    main()
