from __future__ import annotations
import re, unicodedata, json, hashlib
from pydantic import BaseModel, Field

class ExperienceItem(BaseModel):
    company: str
    title: str
    location: str | None = None
    start: str
    end: str
    bullets: list[str] = Field(default_factory=list)

class ProfileSchema(BaseModel):
    name: str
    location: str
    email: str
    phone: str
    linkedin: str
    domains: list[str]
    methods: list[str]
    platforms: list[str]
    security_terms: list[str]
    experience: list[ExperienceItem]
    education: list[str] = Field(default_factory=list)
    awards: list[str] = Field(default_factory=list)

class AnswersSchema(BaseModel):
    global_: dict = Field(alias="global")
    roles: dict = Field(default_factory=dict)
    asked: dict = Field(default_factory=dict)

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "generic"

def to_ascii(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")

def dedupe_list(items: list[str]) -> list[str]:
    seen = set(); out=[]
    for it in items:
        key = to_ascii(it).strip().lower()
        if not key or key in seen: continue
        seen.add(key); out.append(it.strip())
    return out

def prompt_hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]

def has_numbers(s: str) -> bool:
    return bool(re.search(r"\d", s))

def rewrite_bullet(s: str, is_current: bool = False, inject_kw: list[str] | None = None) -> str:
    s = s.strip().rstrip(".")
    if not is_current:
        s = re.sub(r"\b(lead|manage|drive|own|close|build|coach)\b", r"\1d", s, flags=re.I)
    if inject_kw:
        for kw in inject_kw[:2]:
            if kw.lower() not in s.lower():
                s = f"{s}; {kw}"; break
    return s + "."

def extract_keywords(jd_text: str, top_k: int = 60) -> list[str]:
    text = jd_text.lower()
    phrases = re.findall(r"\b([a-z]+(?:\s+[a-z]+){1,3})\b", text)
    singles = re.findall(r"[a-z]{3,}", text)
    bag = phrases + singles
    stop = set("a an the and or to for with of in into on at from that this those these you your our we they i he she it their be is are was were as by about not will can should would could have has had if but so than then when where which who whose whom such etc per via within without among across under over more most less least few many new use used using also only other same own each every either neither both any all some no nor include including includes included open close free strong great fast nice own role job position company team work remote salary pay compensation benefits etc manager director lead junior senior iii ii i".split())
    freq = {}
    for tok in bag:
        if any(w in stop for w in tok.split()): continue
        if len(tok) < 3: continue
        freq[tok] = freq.get(tok, 0) + 1
    ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:top_k]
    return [k for k,_ in ranked]

def md_experience(experience: list[dict], answers: dict) -> str:
    lines=[]
    for role in experience:
        header = f"**{role['company']} — {role['title']} ({role.get('start','')}–{role.get('end','')})**"
        lines.append(header)
        for b in role.get('bullets', []): lines.append(f"- {b}")
        lines.append("")
    return "\n".join(lines).strip()

def role_key(company: str, title: str) -> str:
    return slugify(f"{company}-{title}")

def fill_template(tpl: str, data: dict[str, str]) -> str:
    return tpl.format(**data)
