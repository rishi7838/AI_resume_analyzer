import streamlit as st  #Used for creating a web app with a simple UI
import PyPDF2  #Extracts text from uploaded PDFs.
import spacy  #A powerful NLP (Natural Language Processing) library to analyze text.
from textblob import TextBlob   #Provides grammar and spelling correction.

# Load spaCy English NLP model
nlp = spacy.load("en_core_web_sm")  #used for keyword extration

def extract_text_from_pdf(uploaded_file):
    """Extract text from a PDF file and handle potential issues."""
    reader = PyPDF2.PdfReader(uploaded_file)  #help to open pdf
    text = ""
    
    for page in reader.pages:
        page_text = page.extract_text()  #iterate through each pages
        if page_text:  
            text += page_text + "\n"
    
    return text.strip() if text.strip() else "Could not extract text. Ensure your PDF is not an image-based scan."

def analyze_resume(text):
    """Analyze resume for spelling, grammar, and keywords."""
    doc = nlp(text)

    # Keyword Extraction - Removing duplicates & ensuring relevance
    keywords = list(set([token.text.lower() for token in doc if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop]))

    # Grammar & Spelling Check
    blob = TextBlob(text)  #Uses TextBlob for grammar and spelling correction.
    grammar_feedback = blob.correct() if len(text) < 1000 else "Text is too long for full correction. Consider checking grammar manually."

    # Improvement Suggestions
    suggestions = []
    if len(text) < 300:
        suggestions.append("Your resume seems too short. Consider adding more details about your skills and experience.")
    if "education" not in text.lower():
        suggestions.append("Consider adding an 'Education' section to highlight your academic background.")
    if "experience" not in text.lower():
        suggestions.append("Consider adding a 'Work Experience' section to showcase your past roles.")
    if len(keywords) < 5:
        suggestions.append("Your resume lacks strong keywords. Consider emphasizing important skills and industry terms.")

    return {
        "keywords": keywords[:10],  # Show top 10 unique keywords
        "grammar_feedback": str(grammar_feedback),
        "suggestions": suggestions
    }

# Streamlit UI
st.title("AI Resume Reviewer")
st.write("Upload your resume and get AI-powered feedback .")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"]) #Creates a file upload button in the web app.

if uploaded_file:
    with st.spinner("Extracting text..."):
        resume_text = extract_text_from_pdf(uploaded_file)

    if resume_text.startswith("Could not extract text"):
        st.error(resume_text)
    else:
        with st.spinner("Analyzing resume..."):
            feedback = analyze_resume(resume_text)

        st.subheader("📌 Suggested Keywords")
        st.write(", ".join(feedback["keywords"]) if feedback["keywords"] else "No significant keywords found.")

        st.subheader("✍️ Grammar & Spelling Suggestions")
        st.write(feedback["grammar_feedback"])

        st.subheader("💡 Improvement Suggestions")
        for suggestion in feedback["suggestions"]: #If sections are missing, it suggests adding them.

            st.write(f"- {suggestion}")

st.info("This is a simple resume analyzer using   NLP tools.")
