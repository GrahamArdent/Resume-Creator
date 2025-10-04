# streamlit_app.py
import streamlit as st
from pathlib import Path
import json
from scripts.build_resume import build_pair
from utils import slugify

BASE = Path(__file__).resolve().parent

st.set_page_config(page_title="Resume Creator v3", page_icon="🧰", layout="centered")
st.title("🧰 Resume Creator v3")
st.caption("Paste a job description, choose a primary style, and generate BOTH a tailored resume and a CV.")

with st.form("jd_form"):
    col1, col2 = st.columns([2, 1])
    company = col1.text_input("Company name", value="ACME")
    style = col2.selectbox(
        "Primary Resume Style",
        ["balanced", "executive", "ats", "human"],  # default balanced = ATS+human
        index=0,
        help="Balanced = ATS-friendly + human-readable. CV is always generated in addition."
    )
    jd_text = st.text_area("Job Description (paste)", height=320, placeholder="Paste the full JD here…")
    submitted = st.form_submit_button("Generate Resume + CV")

if submitted:
    if not jd_text.strip():
        st.error("Please paste a job description.")
    else:
        slug = slugify(company)
        result = build_pair(primary_style=style, company_slug=slug, jd_text=jd_text)
        st.success("Generated! Download below.")

        # Primary
        st.subheader("Primary Resume")
        p = Path(result["primary"]["docx"])
        with open(p, "rb") as f:
            st.download_button("Download Primary Resume (DOCX)", f, file_name=p.name,
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        st.caption("Keyword Coverage (Primary)")
        st.json(json.loads(Path(result["primary"]["report"]).read_text(encoding="utf-8")), expanded=False)
        st.caption("ATS Lint (Primary)")
        st.code(Path(result["primary"]["lint"]).read_text(encoding="utf-8"))

        # CV
        st.subheader("CV")
        p2 = Path(result["cv"]["docx"])
        with open(p2, "rb") as f:
            st.download_button("Download CV (DOCX)", f, file_name=p2.name,
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        st.caption("Keyword Coverage (CV)")
        st.json(json.loads(Path(result["cv"]["report"]).read_text(encoding="utf-8")), expanded=False)
        st.caption("ATS Lint (CV)")
        st.code(Path(result["cv"]["lint"]).read_text(encoding="utf-8"))
