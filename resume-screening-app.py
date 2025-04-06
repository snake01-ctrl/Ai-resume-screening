import streamlit as st
import pandas as pd
import re
import PyPDF2
import matplotlib.pyplot as plt
import plotly.express as px
from io import StringIO
import base64

# Define job roles and associated keywords
roles_keywords = {
    "Data Scientist": ["python", "machine learning", "data analysis", "pandas", "numpy", "regression", "classification"],
    "Web Developer": ["html", "css", "javascript", "react", "node.js", "frontend", "backend", "api"],
    "Fitness Trainer": ["exercise", "nutrition", "fitness", "training", "wellness", "strength", "cardio"]
}

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Preprocess the resume text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\W+', ' ', text)
    return text

# Keyword match scoring
def get_keyword_match_score(resume_text, keywords):
    matched_keywords = [kw for kw in keywords if kw.lower() in resume_text]
    score = len(matched_keywords) / len(keywords)
    return score, matched_keywords

# Skill gap analysis
def skill_gap_analysis(keywords, matched_keywords):
    return list(set(keywords) - set(matched_keywords))

# Dummy resume summarizer
def summarize_resume(resume_text):
    words = resume_text.split()
    return " ".join(words[:50]) + "..." if len(words) > 50 else resume_text

# CSV download link
def get_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="resume_screening_results.csv">📥 Download Results as CSV</a>'
    return href

# Streamlit UI
st.set_page_config(page_title="AI Resume Screening", layout="wide")
st.title("🤖 AI-Powered Resume Screening App with Visual Analysis")
st.write("Upload one or more resumes and select a job role to get match analysis, rankings, and charts.")

job_role = st.selectbox("Select a job role", list(roles_keywords.keys()))
uploaded_files = st.file_uploader("Upload resumes (PDF format only)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_results = []
    ranking_results = []

    st.markdown("## 📋 Resume Analysis")
    for uploaded_file in uploaded_files:
        resume_text = extract_text_from_pdf(uploaded_file)
        resume_text_clean = preprocess_text(resume_text)

        score, matched_keywords = get_keyword_match_score(resume_text_clean, roles_keywords[job_role])
        missing_keywords = skill_gap_analysis(roles_keywords[job_role], matched_keywords)
        summary = summarize_resume(resume_text)

        st.subheader(f"📄 Resume: {uploaded_file.name}")
        st.write(f"**Summary:** {summary}")
        st.metric(label="Match Percentage", value=f"{score*100:.2f}%")
        st.write("**Matched Keywords:**", matched_keywords or "No relevant keywords matched.")
        st.write("**Missing Keywords (Skill Gaps):**", missing_keywords or "No skill gaps detected.")

        with st.expander("📌 Suggestions for Improvement"):
            if missing_keywords:
                for skill in missing_keywords:
                    st.markdown(f"- Consider learning or showcasing **{skill}**.")
            else:
                st.write("Your resume aligns very well with the selected role!")

        ranking_results.append({
            "Filename": uploaded_file.name,
            "Match Score (%)": round(score * 100, 2)
        })

        for kw in roles_keywords[job_role]:
            all_results.append({
                "Filename": uploaded_file.name,
                "Keyword": kw,
                "Matched": "Yes" if kw in matched_keywords else "No",
                "Match Score (%)": f"{score*100:.2f}"
            })

    # Rankings
    ranking_df = pd.DataFrame(ranking_results).sort_values(by="Match Score (%)", ascending=False).reset_index(drop=True)
    ranking_df.index += 1
    st.markdown("## 🏆 Resume Rankings")
    st.dataframe(ranking_df, use_container_width=True)

    # Bar Chart of Match Scores
    st.markdown("## 📊 Resume Match Score Chart")
    bar_fig = px.bar(ranking_df, x="Filename", y="Match Score (%)", color="Match Score (%)",
                     color_continuous_scale="Blues", height=400, title="Resume Match Scores")
    st.plotly_chart(bar_fig, use_container_width=True)

    # CSV Export
    result_df = pd.DataFrame(all_results)
    st.markdown("## 📥 Download Match Details")
    st.markdown(get_download_link(result_df), unsafe_allow_html=True)
