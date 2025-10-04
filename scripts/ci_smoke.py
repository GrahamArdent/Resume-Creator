@"
from pathlib import Path
import json, subprocess, sys

BASE = Path(__file__).resolve().parents[1]

def ensure_dirs():
    (BASE / "profile").mkdir(parents=True, exist_ok=True)
    (BASE / "data").mkdir(parents=True, exist_ok=True)

def write_minimal_profile():
    profile = {
        "name": "Graham Hill",
        "location": "Toronto, ON",
        "email": "graham@example.com",
        "phone": "(555) 555-5555",
        "linkedin": "https://www.linkedin.com/in/grahamhillsaas/",
        "domains": ["SaaS", "Cybersecurity"],
        "methods": ["Prospecting", "Discovery", "Negotiation", "Closing"],
        "platforms": ["Salesforce", "HubSpot"],
        "security_terms": ["endpoint", "identity-first", "passwordless"],
        "experience": [
            {
                "company": "SampleCo",
                "title": "Enterprise Account Executive",
                "start": "2022",
                "end": "Present",
                "location": "Remote",
                "bullets": [
                    "Closed 500K TCV 3-year term, unlimited seats.",
                    "Built pipeline and exceeded quota consistently."
                ]
            }
        ],
        "education": ["B.A. (Hons) – University"],
        "awards": ["President's Club"]
    }
    (BASE / "profile" / "profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    answers = {"global": {"extra_keywords": [], "summary_additions": []}, "roles": {}, "asked": {}}
    (BASE / "profile" / "answers.json").write_text(json.dumps(answers, indent=2), encoding="utf-8")

def write_minimal_jd():
    jd = """Company: ExampleCorp
Role: Enterprise Account Executive (SaaS / Cybersecurity)
Requirements: prospecting, discovery, closing, CRM hygiene, endpoint, identity-first
"""
    (BASE / "data" / "job_posting.txt").write_text(jd, encoding="utf-8")

def run_build():
    print("Running smoke build…")
    subprocess.run([sys.executable, str(BASE / "scripts" / "build_resume.py"), "balanced", "ci"], check=True)
    subprocess.run([sys.executable, str(BASE / "scripts" / "build_resume.py"), "cv", "ci"], check=True)
    out = BASE / "outputs" / "ci"
    print("Artifacts:", sorted(p.name for p in out.glob("*")))

if __name__ == "__main__":
    ensure_dirs()
    write_minimal_profile()
    write_minimal_jd()
    run_build()
"@ | Out-File -Encoding utf8 "scripts\ci_smoke.py"
