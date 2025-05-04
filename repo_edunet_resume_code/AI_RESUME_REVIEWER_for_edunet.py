import streamlit as st
import PyPDF2
import spacy

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# ----------- PDF Extraction -----------
def extract_text_from_pdf(uploaded_file):
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip() if text.strip() else None
    except Exception:
        return None

# ----------- Analyzer -----------
def analyze_resume(text):
    doc = nlp(text)
    word_count = len(text.split())
    lower_text = text.lower()

    # --- Keyword Extraction ---
    keywords = list({
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop and token.is_alpha and len(token.text) > 2
    })

    # --- Grammar & Spelling Suggestions (spaCy-only, fast & short) ---
    grammar_feedback = []
    for i, sent in enumerate(doc.sents):
        words = list(sent)
        if not any(tok.pos_ == "VERB" for tok in words):
            grammar_feedback.append(f"⚠️ Sentence {i+1} might be incomplete.")
        elif len(words) > 30:
            grammar_feedback.append(f"✏️ Sentence {i+1} is too long. Consider splitting.")
        if len(grammar_feedback) >= 5:
            break
    if not grammar_feedback:
        grammar_feedback.append("✅ No major grammar issues detected.")

    # --- Structural Suggestions ---
    suggestions = []
    expected_sections = ["education", "experience", "skills", "projects", "certifications"]
    for section in expected_sections:
        if section not in lower_text:
            suggestions.append(f"Consider adding a '{section.capitalize()}' section.")

    if word_count < 100:
        suggestions.append("Your resume is very short. Consider expanding details.")
    elif word_count > 1000:
        suggestions.append("Your resume is quite long. Aim for concise content (ideally 1–2 pages).")

    if len(keywords) < 5:
        suggestions.append("Add more technical and domain-specific keywords.")

    # --- Resume Scoring ---
    score = 0
    score += min(len(keywords), 10) * 2         # 20 points
    score += (5 - len([s for s in expected_sections if s not in lower_text])) * 10  # 50 points
    score += max(0, 10 - len(grammar_feedback)) * 2       # 20 points
    if 300 <= word_count <= 800:
        score += 10  # Ideal length bonus

    return {
        "keywords": keywords[:10],
        "grammar_feedback": grammar_feedback,
        "suggestions": suggestions,
        "score": min(score, 100)
    }

#   Streamlit UI  
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title("📄 AI Resume Analyzer")
st.write("Upload your resume (PDF only) to get smart feedback and a resume score.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting and analyzing resume..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if not resume_text:
        st.error("❌ Could not extract text. Ensure your PDF isn't scanned or image-based.")
    else:
        feedback = analyze_resume(resume_text)

        st.success("✅ Resume Analysis Complete!")

        st.subheader("📌 Top Keywords Detected")
        st.write(", ".join(feedback["keywords"]) if feedback["keywords"] else "No strong keywords found.")

        st.subheader("✍️ Grammar & Spelling Suggestions")
        for line in feedback["grammar_feedback"]:
            st.write(line)

        st.subheader("💡 Improvement Tips")
        for tip in feedback["suggestions"]:
            st.write(f"- {tip}")

        st.subheader("📊 Resume Grade")
        st.markdown(f"**Your Resume Score: {feedback['score']} / 100**")
        if feedback["score"] >= 85:
            st.success("🎉 Excellent! Your resume is strong and well-structured.")
        elif feedback["score"] >= 60:
            st.info("👍 Good, but there's room for improvement.")
        else:
            st.warning("⚠️ Needs work. Consider improving grammar, content, and structure.")

st.info(" Built  by Rishabh chauhan.")
