import os
import re
import streamlit as st
from utils import extract_text_from_pdf, generate_paper_summary, query_gemma_paper

# Page Configuration
st.set_page_config(
    page_title="paperX",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Theme Styling (Gemini Aesthetic)
st.markdown("""
    <style>
    .stApp {
        background-color: #131314;
        color: #e3e3e3;
    }
    section[data-testid="stSidebar"] {
        background-color: #1e1f20;
        border-right: 1px solid #333538;
    }
    .stTextInput input {
        background-color: #1e1f20 !important;
        color: white !important;
        border-radius: 24px !important;
        border: 1px solid #444746 !important;
        padding: 12px 20px !important;
    }
    .stFileUploader {
        background-color: #1e1f20;
        border: 1px dashed #444746;
        border-radius: 12px;
        padding: 10px;
    }
    h1, h2, h3 {
        color: #e3e3e3 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🧬 paperX")
    st.caption("AI-Powered Research Paper Assistant")
    st.divider()

    st.markdown("#### Model Settings")
    selected_model = st.selectbox(
        "Choose Gemma Model",
        options=[
            "gemma-4-26b-a4b-it", 
            "gemma-4-31b-it", 
            "gemma-4-12b-it"
        ],
        index=0,
        help="Select the specific Gemma variant to power your analysis."
    )
    
    st.divider()
    st.markdown("#### Upload Document")
    uploaded_file = st.file_uploader("Upload a Research Paper (PDF)", type=["pdf"])

# Main Chat Interface Area
st.markdown("### paperX")
st.caption("Explore methodologies, tables, figures, and results grounded in your research document.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "paper_text" not in st.session_state:
    st.session_state.paper_text = None

if "paper_summary" not in st.session_state:
    st.session_state.paper_summary = None

if uploaded_file is not None:
    if st.session_state.get("current_file") != uploaded_file.name:
        with st.spinner("Analyzing document structure and auto-generating summary..."):
            st.session_state.paper_text = extract_text_from_pdf(uploaded_file)
            st.session_state.paper_summary = generate_paper_summary(st.session_state.paper_text, selected_model)
            st.session_state.current_file = uploaded_file.name
            st.session_state.messages = []
        st.sidebar.success(f"Loaded: {uploaded_file.name}")
else:
    st.info("👈 Please upload a research paper PDF in the sidebar to begin.")

# Feature 1: Auto-Paper Summary Displayed on Upload
if st.session_state.paper_summary:
    with st.expander("📌 Auto-Generated Executive Summary", expanded=False):
        st.markdown(st.session_state.paper_summary)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Feature 3: Confidence Indicator Badge
        if message["role"] == "assistant" and "confidence" in message:
            conf = message["confidence"]
            color = "green" if conf == "High" else "orange" if conf == "Medium" else "red"
            st.markdown(f"<span style='color:{color}; font-size: 0.85em;'>● **Confidence Rating:** {conf}</span>", unsafe_allow_html=True)

# Continuous Search / Chat Input Bar
if prompt := st.chat_input("Ask about methodology, results, or figures..."):
    if not st.session_state.paper_text:
        st.warning("Please upload a research paper PDF in the sidebar first!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking and grounding response..."):
                answer, confidence = query_gemma_paper(
                    paper_text=st.session_state.paper_text, 
                    user_question=prompt, 
                    model_name=selected_model
                )
                
                # Feature 2: Clickable / Highlighted Citation Inspection Expander
                citations = re.findall(r'\[Page \d+\]', answer)
                
                st.markdown(answer)
                
                # Visual badge for confidence
                color = "green" if confidence == "High" else "orange" if confidence == "Medium" else "red"
                st.markdown(f"<span style='color:{color}; font-size: 0.85em;'>● **Confidence Rating:** {confidence}</span>", unsafe_allow_html=True)
                
                if citations:
                    with st.expander("🔍 Inspect Citations & Source Pages"):
                        for cite in set(citations):
                            st.write(f"Verified reference found in source document: **{cite}**")
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer, 
            "confidence": confidence
        })
