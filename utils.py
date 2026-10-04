import os
import streamlit as st
import pymupdf
from google import genai

# Safely grab the API key from Streamlit secrets (online) or your local environment variables
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Fallback to standard environment variables if not running on Streamlit Cloud
if not api_key:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

# Initialize the Gemini client with the explicit key
client = genai.Client(api_key=api_key)

def extract_text_from_pdf(uploaded_file):
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        full_text += f"\n--- Page {page_num + 1} ---\n"
        full_text += page.get_text()
    return full_text

def query_gemma_paper(paper_text, user_question, model_name='gemma-4-26b-a4b-it'):
    system_prompt = (
        "You are an expert academic research assistant. "
        "Analyze the provided research paper text and answer the user's question accurately. "
        "You must ground your answer strictly in the text provided. "
        "Always reference the specific section or page number where you found the information."
    )
    
    response = client.models.generate_content(
        model=model_name,
        contents=f"Here is the research paper:\n{paper_text}\n\nQuestion: {user_question}",
        config={
            'system_instruction': system_prompt
        }
    )
    
    return response.text
