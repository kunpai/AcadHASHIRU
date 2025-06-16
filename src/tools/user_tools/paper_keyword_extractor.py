import importlib

__all__ = ['PaperKeywordExtractor']


class PaperKeywordExtractor:
    dependencies = [
        "transformers>=4.0.0",
        "keybert>=0.4.0"
    ]

    inputSchema = {
        "name": "PaperKeywordExtractor",
        "description": "Extracts the abstract from LaTeX source, summarizes it, and pulls out keywords.",
        "parameters": {
            "type": "object",
            "properties": {
                "latex_text": {
                    "type": "string",
                    "description": "Full LaTeX source of the paper, including \\begin{abstract}...\\end{abstract}.",
                },
                "max_summary_length": {
                    "type": "integer",
                    "description": "Maximum token length of the generated summary.",
                    "default": 100
                },
                "min_summary_length": {
                    "type": "integer",
                    "description": "Minimum token length of the generated summary.",
                    "default": 20
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of keywords to extract.",
                    "default": 5
                }
            },
            "required": ["latex_text"]
        }
    }

    def run(self, **kwargs):
        latex = kwargs.get("latex_text", "")
        max_len = kwargs.get("max_summary_length", 100)
        min_len = kwargs.get("min_summary_length", 20)
        top_k = kwargs.get("top_k", 5)

        if not latex:
            return {
                "status": "error",
                "message": "Missing required parameter: 'latex_text'",
                "output": None
            }

        try:
            # dynamic imports
            re = importlib.import_module("re")
            pipeline = importlib.import_module("transformers").pipeline
            KeyBERT = importlib.import_module("keybert").KeyBERT

            # extract abstract from LaTeX
            abstract_match = re.search(
                r"(?is)\\begin\{abstract\}(.*?)\\end\{abstract\}",
                latex
            )
            abstract = abstract_match.group(1).strip() if abstract_match else "Abstract not found."

            # summarize
            summarizer = pipeline("summarization", model="t5-small")
            summary = summarizer(
                abstract[:1000],
                max_length=max_len,
                min_length=min_len,
                do_sample=False
            )[0]["summary_text"].strip()

            # extract keywords
            kw_model = KeyBERT()
            kw_pairs = kw_model.extract_keywords(
                abstract,
                top_n=top_k,
                stop_words="english"
            )
            keywords = [kw for kw, _ in kw_pairs]

            return {
                "status": "success",
                "message": "Extracted abstract, summary, and keywords",
                "output": {
                    "abstract": abstract,
                    "summary": summary,
                    "keywords": keywords
                }
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Processing failed: {e}",
                "output": None
            }
