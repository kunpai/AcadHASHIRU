import fitz  
import re
from transformers import pipeline
from keybert import KeyBERT

# Load summarizer and keyword extractor models
summarizer = pipeline("summarization", model="t5-small")
kw_model = KeyBERT()

def extract_abstract_from_pdf(pdf_path):
    """
    Extract the abstract section from a PDF.
    """
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()

        text = re.sub(r'\s+', ' ', text)
        match = re.search(r"(?i)abstract\s*(.*?)\s*(?=introduction|1\s)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return "Abstract not found. Try checking layout or structure."
    except Exception as e:
        return f"Error reading PDF: {e}"

def summarize_text(text, max_words=80):
    """
    Generate a short summary from input text.
    """
    if not text:
        return ""
    input_text = text.strip()[:1000]
    summary = summarizer(input_text, max_length=100, min_length=20, do_sample=False)[0]["summary_text"]
    return summary

def extract_keywords(text, top_k=5):
    """
    Extract top K keywords from text using KeyBERT.
    """
    keywords = kw_model.extract_keywords(text, top_n=top_k, stop_words='english')
    return [kw[0] for kw in keywords]

def format_paper_md(paper):
    return f"""### {paper['title']}
**Authors:** {paper['authors']}  
**Link:** [Read Paper]({paper['url']})  

**Abstract:**  
{paper['abstract']}

---

"""

def save_to_markdown(papers, filename="results.md"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for paper in papers:
                f.write(format_paper_md(paper))
        print(f"\nSaved to {filename}")
    except Exception as e:
        print(f"Failed to save file: {e}")
