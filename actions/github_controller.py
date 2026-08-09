# agent/actions/github_controller.py
# Full GitHub integration for the Developer Agent.
# Actions: create_repo, read_file, push_file, list_repos, create_issue, search_code, get_repo_tree
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

def _get_headers() -> dict:
    token = _load_keys().get("github_api_key", "").strip()
    if not token:
        raise ValueError("GitHub API key not configured in api_keys.json.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def _get(endpoint: str) -> dict:
    import requests
    resp = requests.get(f"https://api.github.com{endpoint}", headers=_get_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()

def _post(endpoint: str, data: dict) -> dict:
    import requests
    resp = requests.post(f"https://api.github.com{endpoint}", headers=_get_headers(), json=data, timeout=15)
    resp.raise_for_status()
    return resp.json()

def _put(endpoint: str, data: dict) -> dict:
    import requests
    resp = requests.put(f"https://api.github.com{endpoint}", headers=_get_headers(), json=data, timeout=15)
    resp.raise_for_status()
    return resp.json()

def github_control(parameters: dict, player=None) -> str:
    """
    Main entry point for GitHub operations.
    Parameters:
      action: create_repo | read_file | push_file | list_repos | create_issue | search_code | get_repo_tree
      owner: str (GitHub username or org)
      repo: str (repository name)
      path: str (file path in repo)
      content: str (file content to push)
      message: str (commit message)
      title: str (issue title)
      body: str (issue body / description)
      query: str (search query)
      name: str (repo name to create)
      description: str (repo description)
      private: bool (make repo private)
    """
    action = (parameters or {}).get("action", "list_repos").lower().strip()
    try:
        if action == "list_repos":
            data = _get("/user/repos?per_page=30&sort=updated")
            repos = [f"{r['full_name']} ({r['visibility']})" for r in data]
            return "Your GitHub repos:\n" + "\n".join(repos) if repos else "No repos found."

        elif action == "create_repo":
            name = parameters.get("name", "").strip()
            if not name:
                return "Error: 'name' is required to create a repo."
            data = _post("/user/repos", {
                "name": name,
                "description": parameters.get("description", ""),
                "private": bool(parameters.get("private", False)),
                "auto_init": True
            })
            return f"Repository created: {data['html_url']}"

        elif action == "read_file":
            owner = parameters.get("owner", "").strip()
            repo = parameters.get("repo", "").strip()
            path = parameters.get("path", "").strip()
            if not all([owner, repo, path]):
                return "Error: 'owner', 'repo', and 'path' are required to read a file."
            data = _get(f"/repos/{owner}/{repo}/contents/{path}")
            content = base64.b64decode(data["content"]).decode("utf-8")
            return f"File: {path}\n\n{content}"

        elif action == "push_file":
            owner = parameters.get("owner", "").strip()
            repo = parameters.get("repo", "").strip()
            path = parameters.get("path", "").strip()
            content = parameters.get("content", "")
            message = parameters.get("message", "Update file via Vani")
            if not all([owner, repo, path, content]):
                return "Error: 'owner', 'repo', 'path', and 'content' are required to push a file."
            # Check if file exists to get SHA
            sha = None
            try:
                existing = _get(f"/repos/{owner}/{repo}/contents/{path}")
                sha = existing.get("sha")
            except Exception:
                pass
            payload = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode()
            }
            if sha:
                payload["sha"] = sha
            _put(f"/repos/{owner}/{repo}/contents/{path}", payload)
            return f"File '{path}' successfully pushed to {owner}/{repo}."

        elif action == "create_issue":
            owner = parameters.get("owner", "").strip()
            repo = parameters.get("repo", "").strip()
            title = parameters.get("title", "").strip()
            body = parameters.get("body", "")
            if not all([owner, repo, title]):
                return "Error: 'owner', 'repo', and 'title' are required to create an issue."
            data = _post(f"/repos/{owner}/{repo}/issues", {"title": title, "body": body})
            return f"Issue created: {data['html_url']}"

        elif action == "search_code":
            query = parameters.get("query", "").strip()
            if not query:
                return "Error: 'query' is required for code search."
            data = _get(f"/search/code?q={query}&per_page=10")
            items = data.get("items", [])
            if not items:
                return f"No code results found for: {query}"
            lines = [f"Code search results for: {query}"]
            for item in items[:8]:
                lines.append(f"- {item['repository']['full_name']}/{item['path']}: {item.get('html_url', '')}")
            return "\n".join(lines)

        elif action == "get_repo_tree":
            owner = parameters.get("owner", "").strip()
            repo = parameters.get("repo", "").strip()
            if not all([owner, repo]):
                return "Error: 'owner' and 'repo' are required to get repo tree."
            data = _get(f"/repos/{owner}/{repo}/git/trees/HEAD?recursive=1")
            tree = data.get("tree", [])
            files = [item["path"] for item in tree if item["type"] == "blob"]
            return f"Files in {owner}/{repo}:\n" + "\n".join(files[:60])

        else:
            return f"Unknown GitHub action: '{action}'. Valid actions: create_repo, read_file, push_file, list_repos, create_issue, search_code, get_repo_tree"

    except Exception as e:
        return f"GitHub operation '{action}' failed: {e}"
