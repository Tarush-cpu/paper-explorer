import os
import streamlit as st
import pymupdf
from google import genai

def get_gemini_client():
    api_key = None
    try:
        if st.secrets and "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        
    if not api_key:
        return None
        
    return genai.Client(api_key=api_key)

def extract_text_from_pdf(uploaded_file):
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page_num in range(len(doc)):
        page = doc[page_num]
        full_text += f"\n--- Page {page_num + 1} ---\n"
        full_text += page.get_text()
    return full_text

def generate_paper_summary(paper_text, model_name='gemma-4-26b-a4b-it'):
    """Generates an executive summary automatically upon upload."""
    client = get_gemini_client()
    if not client:
        return "❌ API Key missing."
    
    prompt = (
        "Analyze the following research paper and provide a concise executive summary with these exact headings:\n"
        "### 🎯 Core Problem\n"
        "### ⚙️️ Methodology\n"
        "### 📊 Key Results\n"
        "### 🚀 Main Contributions\n\n"
        f"Paper text:\n{paper_text[:30000]}" # Limit first ~30k chars for quick summary generation
    )
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    return response.text

def query_gemma_paper(paper_text, user_question, model_name='gemma-4-26b-a4b-it'):
    client = get_gemini_client()
    
    if not client:
        return "❌ Error: No Gemini API Key found!", "Low"
    
    system_prompt = (
        "You are an expert academic research assistant. "
        "Analyze the provided research paper text and answer the user's question accurately. "
        "You must ground your answer strictly in the text provided. "
        "1. Always reference specific pages as [Page X] for citations. "
        "2. At the very end of your response on a new line, provide a confidence rating in this exact format: [Confidence: High], [Confidence: Medium], or [Confidence: Low]."
    )
    
    response = client.models.generate_content(
        model=model_name,
        contents=f"Here is the research paper:\n{paper_text}\n\nQuestion: {user_question}",
        config={
            'system_instruction': system_prompt
        }
    )
    
    answer_text = response.text
    
    # Extract confidence rating
    confidence = "Medium"
    if "[Confidence: High]" in answer_text:
        confidence = "High"
        answer_text = answer_text.replace("[Confidence: High]", "")
    elif "[Confidence: Low]" in answer_text:
        confidence = "Low"
        answer_text = answer_text.replace("[Confidence: Low]", "")
    elif "[Confidence: Medium]" in answer_text:
        confidence = "Medium"
        answer_text = answer_text.replace("[Confidence: Medium]", "")
        
    return answer_text.strip(), confidence
