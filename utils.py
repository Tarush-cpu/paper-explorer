import pymupdf
from google import genai

# Automatically picks up your API key from your environment variables, 
# or you can paste your key directly inside Client(api_key="YOUR_KEY")
client = genai.Client()

def extract_text_from_pdf(uploaded_file):
    doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        full_text += f"\n--- Page {page_num + 1} ---\n"
        full_text += page.get_text()
        
    return full_text

def query_gemma_paper(paper_text, user_question):
    system_prompt = (
        "You are an expert academic research assistant. "
        "Analyze the provided research paper text and answer the user's question accurately. "
        "You must ground your answer strictly in the text provided. "
        "Always reference the specific section or page number where you found the information."
    )
    
    # Using a cloud-hosted Gemma model endpoint via Google AI Studio
    response = client.models.generate_content(
        model='gemma-4-26b-a4b-it',
        contents=f"Here is the research paper:\n{paper_text}\n\nQuestion: {user_question}",
        config={
            'system_instruction': system_prompt
        }
    )
    
    return response.text