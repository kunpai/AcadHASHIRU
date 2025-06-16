from semantic_scholar import search_semantic_scholar
from utils import save_to_markdown, extract_abstract_from_pdf, extract_keywords

def run_tool():
    pdf_path = input("Enter the path to your PDF file: ").strip()

    print("\nExtracting abstract from PDF...")
    abstract = extract_abstract_from_pdf(pdf_path)

    if abstract.startswith("Abort"):
        print(abstract)
        return

    print("\nAbstract Extracted (first 500 chars):\n", abstract[:500], "...")

    # Extract keywords using KeyBERT
    keywords = extract_keywords(abstract, top_k=8)
    query = " ".join(keywords)
    print(f"\nKeywords Used for Search:\n{query}\n")

    # Search Semantic Scholar
    papers = search_semantic_scholar(query, limit=5)

    if not papers:
        print("No papers found. Try adjusting the query.")
        return

    save_to_markdown(papers, "results.md")

if __name__ == "__main__":
    run_tool()
