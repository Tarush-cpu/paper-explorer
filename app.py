import streamlit as st
from utils import extract_text_from_pdf, query_gemma_paper

st.title("📄 Paper Explorer Prototype")
st.write("Upload a research paper PDF and ask questions about its methodology, results, or figures.")

# 1. File Uploader Widget
uploaded_file = st.file_uploader("Upload your Research Paper (PDF)", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Reading and parsing the research paper..."):
        paper_text = extract_text_from_pdf(uploaded_file)
    st.success("Paper successfully read and loaded into memory!")

    # 2. User Question Input Box
    user_question = st.text_input("Ask a question about the paper:")

    if user_question:
        with st.spinner("Gemma 4 is analyzing the paper..."):
            answer = query_gemma_paper(paper_text, user_question)

        # 3. Display the Output
        st.markdown("### Answer:")
        st.write(answer)

