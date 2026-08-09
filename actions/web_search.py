#web_search.py
import json
import sys
from pathlib import Path

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = _get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"


def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _inference_search(query: str) -> str:
    try:
        from core.inference_wrapper import InferenceWrapper
        wrapper = InferenceWrapper()
        return wrapper.generate_text(
            prompt=query,
            system_instruction="You are a web search comparison assistant. Be factual.",
            provider="deepseek"
        )
    except Exception as e:
        raise ValueError(f"Inference search failed: {e}")


def _ddg_search(query: str, max_results: int = 6) -> list[dict]:
    import warnings
    results = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title":   r.get("title",  ""),
                        "snippet": r.get("body",   ""),
                        "url":     r.get("href",   ""),
                    })
        except ImportError as e:
            print(f"[WebSearch] ⚠️ duckduckgo_search import failed: {e}")
            return []
        except Exception as e:
            print(f"[WebSearch] ⚠️ DDG search failed: {e}")
    return results


def _format_ddg(query: str, results: list[dict]) -> str:
    if not results:
        return f"No results found for: {query}"

    lines = [f"Search results for: {query}\n"]
    for i, r in enumerate(results, 1):
        if r.get("title"):   lines.append(f"{i}. {r['title']}")
        if r.get("snippet"): lines.append(f"   {r['snippet']}")
        if r.get("url"):     lines.append(f"   {r['url']}")
        lines.append("")
    return "\n".join(lines).strip()

def _compare(items: list[str], aspect: str) -> str:
    query = (
        f"Compare {', '.join(items)} in terms of {aspect}. "
        "Give specific facts and data."
    )
    try:
        return _inference_search(query)
    except Exception as e:
        print(f"[WebSearch] ⚠️ Gemini compare failed: {e} — falling back to DDG")

    # DDG fallback: fetch results per item and merge
    all_results: dict[str, list] = {}
    for item in items:
        try:
            all_results[item] = _ddg_search(f"{item} {aspect}", max_results=3)
        except Exception:
            all_results[item] = []

    lines = [f"Comparison — {aspect.upper()}", "─" * 40]
    for item in items:
        lines.append(f"\n▸ {item}")
        for r in all_results.get(item, [])[:2]:
            if r.get("snippet"):
                lines.append(f"  • {r['snippet']}")
    return "\n".join(lines)

def web_search(
    parameters:     dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    query  = params.get("query", "").strip()
    mode   = params.get("mode",  "search").lower().strip()
    items  = params.get("items", [])
    aspect = params.get("aspect", "general").strip() or "general"

    if not query and not items:
        return "Please provide a search query, sir."

    if items and mode != "compare":
        mode = "compare"

    if player:
        player.write_log(f"[Search] {query or ', '.join(items)}")

    print(f"[WebSearch] 🔍 Query: {query!r}  Mode: {mode}")
    if mode == "compare":
        return _compare(items, aspect)

    try:
        # 1. Actually perform the web search FIRST
        results = _ddg_search(query)
        search_context = _format_ddg(query, results)
        
        # 2. Use the LLM to synthesize a context-aware answer based on the search results
        from core.inference_wrapper import InferenceWrapper
        wrapper = InferenceWrapper()
        
        prompt = (
            f"The user asked: '{query}'.\n\n"
            f"Here are the live web search results:\n{search_context}\n\n"
            f"Based on the search results above, provide a comprehensive, context-aware answer."
        )
        
        result = wrapper.generate_text(
            prompt=prompt,
            system_instruction="You are a context-aware web search assistant. Synthesize the provided web search results to answer the user's query factually. If the search results do not contain the answer, state that clearly.",
            provider="openai" # Use OpenAI (GPT-4o) for high-quality synthesis, or fallback to openrouter
        )
        print(f"[WebSearch] ✅ Search & Synthesis OK. ({len(results)} results found)")
        return result
    except Exception as e:
        print(f"[WebSearch] ⚠️ Synthesis failed ({e}) — returning raw DDG results...")
        if 'results' in locals() and results:
            return search_context
        return f"Search failed, sir: {e}"
