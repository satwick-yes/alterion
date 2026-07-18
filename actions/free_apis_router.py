# actions/free_apis_router.py

import json
import urllib.request
import urllib.parse
from pathlib import Path
from core.inference_wrapper import inference_client

def free_api_query(
    parameters: dict,
    player=None,
    session_memory=None
):
    """
    Dynamically routes, queries, and parses any of the 405 public APIs in our database.
    """
    query_description = parameters.get("query_description", "").strip()
    api_name = parameters.get("api_name", "").strip()

    if not query_description:
        msg = "Sir, the API query description is missing."
        _speak_and_log(msg, player)
        return msg

    # 1. Load APIs Database
    base_dir = Path(__file__).resolve().parent.parent
    db_path = base_dir / "config" / "free_apis.json"
    
    if not db_path.exists():
        msg = "Sir, the free APIs database config/free_apis.json does not exist."
        _speak_and_log(msg, player)
        return msg
        
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            apis = json.load(f)
    except Exception as e:
        msg = f"Sir, I failed to load the APIs database: {e}"
        _speak_and_log(msg, player)
        return msg

    # 2. Filter Candidate APIs
    candidates = []
    if api_name:
        candidates = [a for a in apis if api_name.lower() in a["name"].lower()]
    
    if not candidates:
        # Keyword filtering to narrow down options for the LLM
        keywords = query_description.lower().split()
        for api in apis:
            score = 0
            desc_lower = api["description"].lower()
            name_lower = api["name"].lower()
            cat_lower = api["category"].lower()
            
            for kw in keywords:
                if len(kw) < 3:
                    continue
                if kw in name_lower:
                    score += 5
                if kw in cat_lower:
                    score += 3
                if kw in desc_lower:
                    score += 2
                    
            if score > 0:
                candidates.append((score, api))
                
        # Sort by match score and take top 12
        candidates = [item[1] for item in sorted(candidates, key=lambda x: x[0], reverse=True)[:12]]

    if not candidates:
        # Default to a few generally useful APIs if no match
        candidates = [a for a in apis if a["name"] in ["Cat Facts", "Dog Facts", "Dogs", "HTTP Cat", "AnimeChan"]]

    # 3. Ask LLM to pick the API and formulate the URL endpoint and parameters
    prompt = f"""
You are the API Routing Engine for Jarvis. The user wants to perform this action: "{query_description}".
Below is a list of candidate APIs that might match this request:

{json.dumps(candidates, indent=2)}

Task:
1. Select the best API from the candidates list.
2. Determine the exact REST endpoint URL to hit (resolve the base URL to its proper endpoint, e.g. "https://catfact.ninja/" becomes "https://catfact.ninja/fact").
3. Output a structured JSON response specifying the HTTP method, final URL, query parameters, and custom headers.

Response JSON format:
{{
  "selected_api": "Name of the API",
  "url": "https://api.example.com/endpoint",
  "method": "GET",
  "params": {{ "param_key": "param_value" }},
  "headers": {{ "Accept": "application/json" }},
  "reason": "Why this API was selected"
}}
"""
    try:
        response_text = inference_client.generate_text(prompt)
        
        # Parse JSON output from LLM
        # Handle potential markdown code blocks
        clean_json = response_text.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_json:
            clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
        call_spec = json.loads(clean_json)
    except Exception as e:
        msg = f"Sir, I failed to match and construct the API call: {e}"
        _speak_and_log(msg, player)
        return msg

    api_to_call = call_spec.get("selected_api", "Unknown")
    target_url = call_spec.get("url", "")
    method = call_spec.get("method", "GET").upper()
    params = call_spec.get("params", {})
    headers = call_spec.get("headers", {})

    if not target_url:
        msg = "Sir, I couldn't formulate a valid target URL for this request."
        _speak_and_log(msg, player)
        return msg

    _speak_and_log(f"Routing query to API '{api_to_call}'...", player)

    # 4. Perform the HTTP Request
    try:
        if params:
            query_string = urllib.parse.urlencode(params)
            if "?" in target_url:
                target_url += "&" + query_string
            else:
                target_url += "?" + query_string

        req = urllib.request.Request(target_url, method=method)
        # Add headers
        for k, v in headers.items():
            req.add_header(k, v)
        # User-agent header to avoid bot blocks
        if "User-Agent" not in headers:
            req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode("utf-8")
            
            # Format raw JSON or text
            try:
                data = json.loads(raw_data)
                formatted_data = json.dumps(data, indent=2)
            except Exception:
                data = raw_data
                formatted_data = raw_data
    except Exception as e:
        msg = f"Sir, the API call to {api_to_call} failed: {e}"
        _speak_and_log(msg, player)
        return msg

    # 5. Ask LLM to format the response into a spoken sentence
    summary_prompt = f"""
You are Jarvis. You successfully queried the public API "{api_to_call}" to answer the user's request: "{query_description}".

The API returned the following raw response:
{formatted_data}

Provide a polite, natural, and helpful spoken response summarizing the information retrieved for the user. Keep it conversational.
"""
    try:
        spoken_response = inference_client.generate_text(summary_prompt)
        spoken_response = spoken_response.strip()
    except Exception:
        spoken_response = f"Sir, I retrieved this response from {api_to_call}: {str(formatted_data)[:200]}"

    _speak_and_log(spoken_response, player)
    
    if session_memory:
        try:
            session_memory.set_last_search(
                query=query_description,
                response=spoken_response
            )
        except Exception:
            pass

    return spoken_response

def _speak_and_log(message: str, player=None):
    if player:
        try:
            player.write_log(f"JARVIS: {message}")
        except Exception:
            pass
