# agent/actions/hf_specialist.py
# Hugging Face Inference API for specialized NLP micro-tasks.
# Actions: sentiment | ner | caption | summarize | zero_shot
import json, sys, base64
from pathlib import Path

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

def _load_keys() -> dict:
    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _call_hf(model: str, payload: dict) -> dict:
    import requests
    token = _load_keys().get("huggingface_api_key", "").strip()
    if not token:
        raise ValueError("Hugging Face API key not configured.")
    resp = requests.post(
        f"https://api-inference.huggingface.co/models/{model}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=30
    )
    resp.raise_for_status()
    return resp.json()

def hf_specialist(parameters: dict, player=None) -> str:
    """
    Performs specialized NLP tasks via Hugging Face.
    Parameters:
      action: sentiment | ner | caption | summarize | zero_shot
      text: str (input text)
      image_path: str (for caption action)
      labels: list[str] (for zero_shot action)
    """
    action = (parameters or {}).get("action", "sentiment").lower().strip()
    text = (parameters or {}).get("text", "").strip()

    try:
        if action == "sentiment":
            if not text:
                return "Error: 'text' is required for sentiment analysis."
            result = _call_hf("cardiffnlp/twitter-roberta-base-sentiment-latest", {"inputs": text})
            if isinstance(result, list) and result:
                scores = sorted(result[0], key=lambda x: x["score"], reverse=True)
                top = scores[0]
                label_map = {"LABEL_0": "Negative", "LABEL_1": "Neutral", "LABEL_2": "Positive"}
                label = label_map.get(top["label"], top["label"])
                return f"Sentiment: {label} ({top['score']*100:.1f}% confidence)"
            return f"Sentiment result: {result}"

        elif action == "ner":
            if not text:
                return "Error: 'text' is required for Named Entity Recognition."
            result = _call_hf("dbmdz/bert-large-cased-finetuned-conll03-english", {"inputs": text})
            if isinstance(result, list):
                entities = [f"{e['word']} [{e['entity_group']}]" for e in result if isinstance(e, dict)]
                return "Entities found:\n" + "\n".join(entities) if entities else "No named entities found."
            return str(result)

        elif action == "caption":
            image_path = (parameters or {}).get("image_path", "").strip()
            if not image_path:
                return "Error: 'image_path' is required for image captioning."
            import requests as req
            token = _load_keys().get("huggingface_api_key", "").strip()
            with open(image_path, "rb") as f:
                img_data = f.read()
            resp = req.post(
                "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large",
                headers={"Authorization": f"Bearer {token}"},
                data=img_data,
                timeout=30
            )
            result = resp.json()
            if isinstance(result, list) and result:
                return f"Image caption: {result[0].get('generated_text', str(result))}"
            return f"Caption result: {result}"

        elif action == "summarize":
            if not text:
                return "Error: 'text' is required for summarization."
            result = _call_hf("facebook/bart-large-cnn", {"inputs": text, "parameters": {"max_length": 150, "min_length": 30}})
            if isinstance(result, list) and result:
                return f"Summary:\n{result[0].get('summary_text', str(result))}"
            return str(result)

        elif action == "zero_shot":
            labels = (parameters or {}).get("labels", [])
            if not text or not labels:
                return "Error: 'text' and 'labels' are required for zero-shot classification."
            result = _call_hf("facebook/bart-large-mnli", {"inputs": text, "parameters": {"candidate_labels": labels}})
            if isinstance(result, dict):
                pairs = sorted(zip(result.get("labels", []), result.get("scores", [])), key=lambda x: x[1], reverse=True)
                lines = [f"{label}: {score*100:.1f}%" for label, score in pairs]
                return "Zero-shot classification:\n" + "\n".join(lines)
            return str(result)

        else:
            return f"Unknown HF action: '{action}'. Valid: sentiment, ner, caption, summarize, zero_shot"

    except Exception as e:
        return f"Hugging Face '{action}' failed: {e}"
