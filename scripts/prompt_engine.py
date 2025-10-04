from __future__ import annotations
import os, json, hashlib
from utils import extract_keywords, dedupe_list

def _get_openai_client():
    key = os.environ.get("OPENAI_API_KEY")
    if not key: return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=key)
    except Exception:
        try:
            import openai
            openai.api_key = key
            return openai
        except Exception:
            return None

def rank_keywords_with_llm(jd_text: str, candidates: list[str]) -> list[str]:
    client = _get_openai_client()
    if not client: return candidates[:40]
    prompt = f"""You are an ATS expert. Given a job description, select and rank the 35–45 MOST IMPORTANT skills/keywords
that would impact resume parsing and keyword matching. Return a JSON array of strings only.

JD:
{jd_text[:4000]}
Candidates:
{candidates[:80]}
"""
    try:
        try:
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], temperature=0.2)
            txt = resp.choices[0].message.content.strip()
        except Exception:
            resp = client.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role":"user","content":prompt}], temperature=0.2)
            txt = resp["choices"][0]["message"]["content"].strip()
        arr = json.loads(txt)
        if isinstance(arr, list):
            return dedupe_list([str(x) for x in arr])[:45]
    except Exception:
        pass
    return candidates[:40]

def generate_questions(jd_text: str, existing: dict | None = None, **kwargs):
    asked = set()
    if existing and isinstance(existing, dict):
        asked |= {h for h in existing.get("asked_prompts", [])}
    kws = extract_keywords(jd_text)
    qs = []
    if any("quota" in k for k in kws):
        qs.append("What was your average quota attainment by role (%, quarters/years)?")
    if any("pipeline" in k for k in kws):
        qs.append("What was your average qualified pipeline ($) and win rate?")
    if any("government" in k or "public sector" in k for k in kws):
        qs.append("List notable public-sector/enterprise logos relevant to this posting.")
    if any("rfp" in k for k in kws):
        qs.append("Provide specific RFP wins or contributions (value, year).")
    out = []
    for q in qs:
        h = hashlib.sha1(q.encode("utf-8")).hexdigest()[:16]
        if h in asked: continue
        out.append({"id":h,"prompt":q})
    return out
