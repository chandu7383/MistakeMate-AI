import os
import streamlit as st
from dotenv import load_dotenv

from db import init_db, save_analysis, get_history
from ai import analyze_answer
from ocr import extract_text_from_image, extract_text_from_pdf

load_dotenv()
init_db()

st.set_page_config(page_title="MistakeMate AI", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.main-title {font-size: 42px; font-weight: 800;}
.subtitle {font-size: 18px; color: #666;}
.card {padding: 18px; border-radius: 14px; border: 1px solid #ddd; margin-bottom: 12px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 MistakeMate AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Find the mistake. Understand the mistake. Learn from the mistake.</div>', unsafe_allow_html=True)

if not os.getenv("OPENAI_API_KEY"):
    st.warning("OPENAI_API_KEY is missing. Add it to your .env file before using AI analysis.")

tab1, tab2, tab3 = st.tabs(["🔍 Check Answer", "📊 My Progress", "ℹ️ About"])

with tab1:
    st.subheader("1. Enter the question")
    question = st.text_area(
        "Question",
        placeholder="Example: What is Machine Learning?",
        height=100
    )

    st.subheader("2. Enter or upload the student's answer")
    input_mode = st.radio("Answer input", ["Type answer", "Upload image", "Upload PDF"], horizontal=True)

    answer = ""

    if input_mode == "Type answer":
        answer = st.text_area(
            "Student Answer",
            placeholder="Type the student's answer here...",
            height=220
        )

    elif input_mode == "Upload image":
        image_file = st.file_uploader("Upload answer image", type=["png", "jpg", "jpeg"])
        if image_file:
            st.image(image_file, caption="Uploaded answer", use_container_width=True)
            if st.button("📖 Read image"):
                with st.spinner("Reading answer..."):
                    answer = extract_text_from_image(image_file)
                st.session_state["ocr_answer"] = answer
        answer = st.session_state.get("ocr_answer", answer)
        if answer:
            st.text_area("Extracted text", value=answer, height=220, key="image_text")

    elif input_mode == "Upload PDF":
        pdf_file = st.file_uploader("Upload answer PDF", type=["pdf"])
        if pdf_file:
            if st.button("📖 Read PDF"):
                with st.spinner("Reading PDF..."):
                    answer = extract_text_from_pdf(pdf_file)
                st.session_state["pdf_answer"] = answer
        answer = st.session_state.get("pdf_answer", answer)
        if answer:
            st.text_area("Extracted text", value=answer, height=220, key="pdf_text")

    if st.button("🚀 Find My Mistakes", type="primary", use_container_width=True):
        final_answer = answer.strip()
        if input_mode == "Type answer":
            final_answer = answer.strip()

        if not question.strip():
            st.error("Please enter the question.")
        elif not final_answer:
            st.error("Please provide an answer.")
        elif not os.getenv("OPENAI_API_KEY"):
            st.error("Please configure OPENAI_API_KEY in .env.")
        else:
            with st.spinner("🤖 AI teacher is checking the answer..."):
                try:
                    result = analyze_answer(question, final_answer)
                    st.session_state["last_result"] = result
                    save_analysis(question, final_answer, result)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")

    result = st.session_state.get("last_result")

    if result:
        st.divider()
        st.subheader("📋 AI Evaluation")

        c1, c2, c3 = st.columns(3)
        c1.metric("Score", f"{result.get('score', 0)}/100")
        c2.metric("Status", result.get("overall_status", "Unknown"))
        c3.metric("Mistakes", len(result.get("mistakes", [])))

        st.markdown("### ❌ Mistakes Found")
        mistakes = result.get("mistakes", [])

        if not mistakes:
            st.success("🎉 No major mistakes found. Your answer looks good!")
        else:
            for i, m in enumerate(mistakes, 1):
                with st.expander(f"{i}. {m.get('type', 'Mistake')}"):
                    st.write("**Wrong / weak part:**", m.get("wrong_part", ""))
                    st.write("**Why:**", m.get("why_wrong", ""))
                    st.write("**Correct version:**", m.get("correct_version", ""))

        st.markdown("### 🧠 Learn From Your Mistake")
        st.info(result.get("simple_explanation", ""))

        st.markdown("### 💡 Easy Example")
        st.success(result.get("easy_example", ""))

        st.markdown("### 🧠 Remember Tip")
        st.warning(result.get("remember_tip", ""))

        st.markdown("### 📝 Practice Question")
        st.write(result.get("practice_question", ""))

        st.markdown("### 🎯 Weak Topics")
        for topic in result.get("weak_topics", []):
            st.write(f"- {topic}")

with tab2:
    st.subheader("📊 Your Recent Learning History")
    history = get_history(20)

    if not history:
        st.info("No analyses yet. Check your first answer in the Check Answer tab.")
    else:
        for item in history:
            with st.expander(f"{item['created_at']} — {item['status']} — {item['score']}/100"):
                st.write("**Question:**", item["question"])
                st.write("**Answer:**", item["answer"])
                st.write("**Mistakes:**", item["mistake_count"])

with tab3:
    st.subheader("About MistakeMate AI")
    st.write("""
MistakeMate AI is an educational assistant that does more than mark an answer
correct or incorrect. It identifies mistake types, explains why an answer is
wrong, gives a corrected version, provides a simple example, and creates a
practice question.

This is a college-project prototype. AI evaluation should be treated as
learning assistance, not as an official examination grade.
""")