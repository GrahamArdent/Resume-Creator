# scripts/run_interactive_qna.py
from prompt_engine import generate_questions
from utils import slugify
import json, os

def main():
    jd_path = input("Paste JD file path: ").strip()
    company = input("Company name: ").strip()
    style = "executive"
    with open(jd_path, 'r', encoding='utf-8') as f:
        jd_text = f.read()

    # load profile + answers
    with open("profile/profile.json","r",encoding="utf-8") as f:
        profile = json.load(f)
    if os.path.exists("profile/answers.json"):
        answers = json.load(open("profile/answers.json","r",encoding="utf-8"))
    else:
        answers = {}

    resume_text = " ".join([r['title'] for r in profile.get("experience",[])])
    qs = generate_questions(jd_text, resume_text, profile, answers, style)
    print("\nQuestions to answer:")
    for q in qs:
        print("-", q['prompt'])

if __name__ == "__main__":
    main()
