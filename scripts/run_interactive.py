# scripts/run_interactive.py
from pathlib import Path
import sys, textwrap, subprocess, os

BASE = Path(__file__).resolve().parents[1]
jd_path = BASE / "data" / "job_posting.txt"
builder = BASE / "scripts" / "build_resume.py"
styles = {"1": "executive", "2": "balanced", "3": "ats"}

print("\n=== Paste the job posting below. End input with a single line containing only 'END'. ===")
print("(Tip: right-click to paste in Windows Terminal / PowerShell)")
lines = []
while True:
    try:
        line = input()
    except EOFError:
        break
    if line.strip() == "END":
        break
    lines.append(line)

jd = "\n".join(lines).strip()
if not jd:
    print("No job posting provided. Exiting.")
    sys.exit(1)

jd_path.write_text(jd, encoding="utf-8")
print(f"\nSaved job posting to: {jd_path}")

print(textwrap.dedent("""
Select resume style:
  [1] Executive   (recommended for most)
  [2] Balanced    (human-friendly, still ATS-safe)
  [3] ATS         (parser-first, super minimal)
"""))
choice = input("Enter 1, 2, or 3: ").strip()
style = styles.get(choice, "executive")
print(f"\nBuilding style: {style} ...\n")

# Run builder
cmd = [sys.executable, str(builder), style]
subprocess.run(cmd, check=True)

out = BASE / "outputs"
print("Done.\nGenerated files in:", out)
for p in sorted(out.glob(f"Resume - * - {style.capitalize()}.docx")):
    print("  -", p)
for p in sorted(out.glob(f"questions_{style}.md")):
    print("  -", p)
for p in sorted(out.glob(f"match_report_{style}.json")):
    print("  -", p)
