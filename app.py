import os
import streamlit as st
from utils import extract_text_from_pdf, query_gemma_paper

# 1. Page Configuration (Wide layout for a dashboard feel)
st.set_page_config(
    page_title="paperX",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom Dark Theme Styling (Gemini Aesthetic)
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

# 3. Sidebar Configuration (paperX Branding & Controls)
with st.sidebar:
    st.markdown("### 🧬 paperX")
    st.caption("AI-Powered Research Paper Assistant")
    st.divider()

    # Dropdown menu for model selection
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

# 4. Main Chat Interface Area
st.markdown("### paperX")
st.caption("Explore methodologies, tables, figures, and results grounded in your research document.")

# Initialize session state to store chat history and extracted paper text
if "messages" not in st.session_state:
    st.session_state.messages = []

if "paper_text" not in st.session_state:
    st.session_state.paper_text = None

# Handle PDF Upload state
if uploaded_file is not None:
    # If a new file is uploaded, parse it and reset chat history if needed
    if st.session_state.get("current_file") != uploaded_file.name:
        with st.spinner("Analyzing document structure and text..."):
            st.session_state.paper_text = extract_text_from_pdf(uploaded_file)
            st.session_state.current_file = uploaded_file.name
            st.session_state.messages = []  # Clear chat for new paper
        st.sidebar.success(f"Loaded: {uploaded_file.name}")
else:
    st.info("👈 Please upload a research paper PDF in the sidebar to begin chatting.")

# Display existing chat messages (Gemini continuous style)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Continuous Search / Chat Input Bar (Gemini Style)
if prompt := st.chat_input("Ask about methodology, results, or figures..."):
    if not st.session_state.paper_text:
        st.warning("Please upload a research paper PDF in the sidebar first!")
    else:
        # Append user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response using the selected model
        with st.chat_message("assistant"):
            with st.spinner("Thinking and grounding response in text..."):
                answer = query_gemma_paper(
                    paper_text=st.session_state.paper_text, 
                    user_question=prompt, 
                    model_name=selected_model
                )
                st.markdown(answer)
        
        # Append assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": answer})
