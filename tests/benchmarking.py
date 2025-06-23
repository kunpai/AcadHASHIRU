import os
import json
import random
import time
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import argparse
from gradio_client import Client
from google import genai
from google.genai import types

API_KEY = os.getenv("API_KEY", "")
random.seed(12345)


def get_client(model_name: str):
    """
    Initialize and return a client based on model_name.
    """
    if model_name == "hashiru":
        client = Client("http://127.0.0.1:7860/")
        client.predict(
            modeIndexes=[
                "ENABLE_AGENT_CREATION",
                "ENABLE_LOCAL_AGENTS",
                "ENABLE_CLOUD_AGENTS",
                "ENABLE_TOOL_CREATION",
                "ENABLE_TOOL_INVOCATION",
                "ENABLE_RESOURCE_BUDGET",
                "ENABLE_ECONOMY_BUDGET",
            ],
            api_name="/update_model"
        )
        return client

    elif model_name == "flash2.0":
        return genai.Client(api_key=API_KEY)

    else:
        raise ValueError(f"Unsupported model: {model_name}")


def call_api(client, model_name: str, prompt: str, history=None, tries=0):
    """
    Send prompt (and optional history) to the appropriate API and return response content and updated history.
    Retries up to 3 times on error.
    """
    if tries > 3:
        print("Error: too many tries")
        return "", history

    start = time.time()
    if model_name == "hashiru":
        response, new_history = client.predict(
            {"text": prompt, "files": []},
            history,
            api_name="/chat"
        )
        content = _extract_from_history(new_history)

    elif model_name == "flash2.0":
        safety_settings = [
            {"category": cat, "threshold": "BLOCK_NONE"}
            for cat in [
                "HARM_CATEGORY_HARASSMENT",
                "HARM_CATEGORY_HATE_SPEECH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "HARM_CATEGORY_DANGEROUS_CONTENT",
            ]
        ]
        try:
            gen_output = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    safety_settings=safety_settings,
                ),
            )
            content = gen_output.text
            new_history = history

        except Exception as e:
            time.sleep(60)
            return call_api(client, model_name, prompt, history, tries + 1)
    else:
        content, new_history = "", history

    elapsed = time.time() - start
    print(f"→ API call took {elapsed:.2f}s")
    return content, new_history


def _extract_from_history(history):
    """
    Helper to pull the last assistant content from chat history.
    """
    if not history:
        return ""
    for turn in reversed(history):
        if turn.get("role") == "assistant":
            if text := turn.get("content"):
                return text
            if fr := turn.get("function_response"):
                return fr.get("result", {}).get("output", "")
    return ""


def benchmark_paper_reviews(
    csv_path,
    model_name,
    id_col="ID",
    text_col="concatenated_text",
    num_samples=None,
    offset=0,
    output_dir="results"
):
    """
    Benchmark agent performance on paper reviews and write JSONL with prompt repetition.
    """
    df = pd.read_csv(csv_path, sep="|")
    if offset or num_samples:
        end = offset + num_samples if num_samples else None
        df = df.iloc[offset:end].reset_index(drop=True)

    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(output_dir, f"paper_review_{model_name}_{ts}.jsonl")
    print(f"Results will be written to {out_file}")

    client = get_client(model_name)
    results = []

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        paper_id = row[id_col]
        title = row.get("Title", "")
        iter_start = time.time()
        prompt = (
            "Review the following paper for International Conference on Learning Representations (ICLR) 2023. "
            "Remember you need to make 3 reviewer agents for each paper. "
            "GIVE A FINAL DECISION in the form of \"FINAL DECISION: <Accept/Reject>\". "
            f"The paper title is: {title}\n\n" + row[text_col]
        )

        print(f"[{idx+1}/{len(df)}] Reviewing ID={paper_id}")
        history = []
        content, history = call_api(client, model_name, prompt, history)

        # ensure final decision
        while "FINAL DECISION" not in content.upper():
            time.sleep(5)
            content, history = call_api(
                client,
                model_name,
                "Please finish the review and give the FINAL DECISION line.",
                history
            )

        elapsed_time = time.time() - iter_start
        # Read src/models/models.json
        with open("src/models/models.json", "r") as f:
            reviewer_agents_data = json.load(f)
        result = {
            "paper_id": paper_id,
            "prompt": prompt,
            "agent_review": history,
            "ground_truth": row.get("Decision"),
            "response_history": content,
            "elapsed_time": elapsed_time,
            "reviewer_agents": reviewer_agents_data
        }

        with open(out_file, "a") as fo:
            fo.write(json.dumps(result) + "\n")

        results.append(result)
        time.sleep(5)

    print("Benchmark complete.")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Run paper-review benchmark.")
    parser.add_argument("--csv", "-c", type=str, default="tests/ICLR_2023.csv")
    parser.add_argument("--model", "-m", type=str, default="hashiru", choices=["hashiru", "flash2.0"])
    parser.add_argument("--offset", "-o", type=int, default=0)
    parser.add_argument("--num_samples", "-n", type=int, help="Number of papers to sample", default=None)
    parser.add_argument("--output_dir", "-d", type=str, default="results")
    args = parser.parse_args()

    benchmark_paper_reviews(
        csv_path=args.csv,
        model_name=args.model,
        num_samples=args.num_samples,
        offset=args.offset,
        output_dir=args.output_dir
    )
