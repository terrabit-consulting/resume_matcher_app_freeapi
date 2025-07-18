import streamlit as st
import requests
import time

# ✅ Secure Hugging Face API key
HF_API_KEY = st.secrets["HUGGINGFACE_API_KEY"]
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# 🎯 Universal prompt caller
def call_huggingface_model(prompt):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 600,
            "temperature": 0.7
        }
    }
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{HF_MODEL}",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        generated = response.json()
        if isinstance(generated, list) and "generated_text" in generated[0]:
            return generated[0]["generated_text"]
        else:
            return "⚠️ Response format error."
    else:
        return f"❌ Hugging Face API Error: {response.status_code}\n{response.text}"

# 🔍 Compare JD and Resume
def compare_resume(jd_text, resume_text):
    prompt = f"""
You are a helpful recruiter assistant.

Compare the resume below to the job description. Return:

1. 📛 Candidate Name (if known)
2. ✅ Match Score (percentage)
3. 🔍 Reasons for the score
4. ⚠️ Warning if the score < 70%

Don't generate WhatsApp or Email yet.

Job Description:
{jd_text}

Resume:
{resume_text}
"""
    return call_huggingface_model(prompt)

# 💬 Generate WhatsApp, Email, and Screening Questions
def generate_followup(jd_text, resume_text):
    prompt = f"""
Based on the following JD and resume, generate:

1. 📱 WhatsApp message (casual, short)
2. 📧 Email message (formal, respectful)
3. 🧠 Screening questions (3 to 5 max)

Job Description:
{jd_text}

Resume:
{resume_text}
"""
    return call_huggingface_model(prompt)

# 🖥️ Streamlit App UI
st.set_page_config(page_title="Free Resume Matcher", layout="centered")
st.title("📄 Resume Matcher Bot (100% Free - Hugging Face API)")
st.write("Upload a JD and multiple resumes. Match score, generate messages — all free.")

# 📂 Upload Files
jd_file = st.file_uploader("📌 Upload Job Description", type=["txt", "pdf", "docx"])
resume_files = st.file_uploader("📥 Upload Candidate Resumes", type=["txt", "pdf", "docx"], accept_multiple_files=True)

# 🚀 Run Matching
if st.button("Run Matching") and jd_file and resume_files:
    jd_text = jd_file.read().decode("utf-8", errors="ignore")

    for idx, resume_file in enumerate(resume_files):
        resume_text = resume_file.read().decode("utf-8", errors="ignore")

        with st.spinner(f"🔍 Matching {resume_file.name}..."):
            result = compare_resume(jd_text, resume_text)

        st.markdown("---")
        st.subheader(f"📛 {resume_file.name}")
        st.markdown(result)

        followup_key = f"followup_{idx}"
        if st.button(f"✅ Generate WhatsApp/Email/Questions for {resume_file.name}", key=followup_key):
            with st.spinner("Generating messages..."):
                followup = generate_followup(jd_text, resume_text)
                st.success("🎉 Messages generated!")
                st.markdown(followup)
