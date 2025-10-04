from __future__ import annotations
from pathlib import Path
import json
BASE = Path(__file__).resolve().parents[1]
ANSWERS = BASE / "profile" / "answers.json"
def main():
    data = json.loads(ANSWERS.read_text(encoding="utf-8"))
    g = data.setdefault("global", {})
    lst = g.setdefault("summary_additions", [])
    print("=== Curate summary additions (interactive) ===")
    print("Rules: keep 6–24 words, single sentence, crisp & quantified where possible.\n")
    cleaned = []
    for item in lst:
        s = item.strip().rstrip(".")
        if len(s.split()) > 30: s = " ".join(s.split()[:24])
        cleaned.append(s.capitalize() + ".")
    g["summary_additions"] = cleaned
    ANSWERS.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved. summary_additions = {len(cleaned)} item(s).")
if __name__ == "__main__":
    main()
