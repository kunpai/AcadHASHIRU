import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")

def search_semantic_scholar(query, limit=5):
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {
        "x-api-key": API_KEY
    }
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,abstract,url"
    }

    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    papers = response.json().get("data", [])
    return [
        {
            "title": p.get("title", "No title"),
            "authors": ", ".join([a.get("name", "") for a in p.get("authors", [])]),
            "abstract": p.get("abstract", "No abstract available."),
            "url": p.get("url", "No link available")
        }
        for p in papers
    ]
