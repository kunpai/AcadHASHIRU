import importlib

__all__ = ['SemanticScholarTool']


class SemanticScholarTool:
    dependencies = [
        "requests>=2.0.0",
        "python-dotenv>=0.19.0"
    ]

    inputSchema = {
        "name": "SemanticScholarTool",
        "description": "Searches Semantic Scholar for academic papers based on a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for papers on Semantic Scholar.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of papers to retrieve. Default is 5.",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }

    def run(self, **kwargs):
        query = kwargs.get("query")
        limit = kwargs.get("limit", 5)

        if not query:
            return {
                "status": "error",
                "message": "Missing required parameter: 'query'",
                "output": None
            }

        try:
            # dynamic imports
            requests = importlib.import_module("requests")
            dotenv = importlib.import_module("dotenv")
            os = importlib.import_module("os")

            # load environment
            dotenv.load_dotenv()
            api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
            if not api_key:
                return {
                    "status": "error",
                    "message": "SEMANTIC_SCHOLAR_API_KEY not found in environment",
                    "output": None
                }

            base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            headers = {"x-api-key": api_key}
            params = {
                "query": query,
                "limit": limit,
                "fields": "title,authors,abstract,url"
            }

            resp = requests.get(base_url, headers=headers, params=params)
            if resp.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Semantic Scholar API returned {resp.status_code}",
                    "output": None
                }

            data = resp.json().get("data", [])
            papers = []
            for p in data:
                authors = [a.get("name", "") for a in p.get("authors", [])]
                papers.append({
                    "title": p.get("title", "No title"),
                    "authors": authors,
                    "abstract": p.get("abstract", "No abstract available."),
                    "url": p.get("url", "No link available")
                })

            return {
                "status": "success",
                "message": f"Found {len(papers)} paper(s) on Semantic Scholar",
                "output": papers
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Semantic Scholar search failed: {str(e)}",
                "output": None
            }
