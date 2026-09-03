import threading
from actions.file_processor import file_processor
from actions.flight_finder     import flight_finder
from actions.open_app          import open_app
from actions.weather_report    import weather_action
from actions.send_message      import send_message

from actions.computer_settings import computer_settings
from actions.screen_processor  import screen_process
from actions.youtube_video     import youtube_video

from actions.file_controller   import file_controller
from actions.code_helper       import code_helper
from actions.dev_agent         import dev_agent
from actions.web_search        import web_search as web_search_action

from actions.vision_computer_use import advanced_computer_use

from actions.presentation_maker import create_presentation
from actions.report_maker      import create_report
from actions.system_shell      import run_system_shell
from actions.free_apis_router  import free_api_query
from actions.mobile_control    import mobile_control
from actions.phone_link_controller import phone_link_call
from actions.phone_controller  import make_phone_call
from actions.task_library import execute_hardcoded_task
from actions.llm_brains import (
    run_gemini_brain,
    run_openrouter_brain,
    run_nvidia_brain,
    run_openai_brain,
    run_groq_brain,
    run_deepseek_brain,
    run_cerebras_brain,
    run_mistral_brain,
    run_sambanova_brain
)
from actions.github_controller import github_control
from actions.audio_transcriber import transcribe_audio
from actions.hf_specialist import hf_specialist
from actions.architect_3d import generate_3d_model
from actions.deep_learner import learn_topic_deeply
class WorkerManager:
    @staticmethod
    def dispatch(delegate_name, args, player, speak, async_callback=None):
        print(f"[WorkerManager] Dispatching to {delegate_name} with args: {args}")
        task = args.get("task", "").lower()
        
        # Intercept hardcoded tasks first
        result = execute_hardcoded_task(task)
        if result:
            return result
            
        if delegate_name == "end_phone_call":
            from actions.phone_link_controller import end_phone_call
            return end_phone_call(args, player, speak)

            
        if delegate_name == "delegate_to_operator":
            return WorkerManager._run_operator(task, args, player, speak, async_callback)
        elif delegate_name == "delegate_to_researcher":
            return WorkerManager._run_researcher(task, args, player, speak, async_callback)
        elif delegate_name == "delegate_to_developer":
            return WorkerManager._run_developer(task, args, player, speak, async_callback)
        elif delegate_name == "delegate_to_creator":
            return WorkerManager._run_creator(task, args, player, speak, async_callback)
        elif delegate_name == "delegate_to_gemini_brain":
            return WorkerManager._run_in_background(run_gemini_brain, {"parameters": args, "player": player}, async_callback, "GeminiBrain")
        elif delegate_name == "delegate_to_openrouter_brain":
            return WorkerManager._run_in_background(run_openrouter_brain, {"parameters": args, "player": player}, async_callback, "OpenRouterBrain")
        elif delegate_name == "delegate_to_nvidia_brain":
            return WorkerManager._run_in_background(run_nvidia_brain, {"parameters": args, "player": player}, async_callback, "NvidiaBrain")
        elif delegate_name == "delegate_to_openai_brain":
            return WorkerManager._run_in_background(run_openai_brain, {"parameters": args, "player": player}, async_callback, "OpenAIBrain")
        elif delegate_name == "delegate_to_groq_brain":
            return WorkerManager._run_in_background(run_groq_brain, {"parameters": args, "player": player}, async_callback, "GroqBrain")
        elif delegate_name == "delegate_to_deepseek_brain":
            return WorkerManager._run_in_background(run_deepseek_brain, {"parameters": args, "player": player}, async_callback, "DeepSeekBrain")
        elif delegate_name == "delegate_to_cerebras_brain":
            return WorkerManager._run_in_background(run_cerebras_brain, {"parameters": args, "player": player}, async_callback, "CerebrasBrain")
        elif delegate_name == "delegate_to_mistral_brain":
            return WorkerManager._run_in_background(run_mistral_brain, {"parameters": args, "player": player}, async_callback, "MistralBrain")
        elif delegate_name == "delegate_to_sambanova_brain":
            return WorkerManager._run_in_background(run_sambanova_brain, {"parameters": args, "player": player}, async_callback, "SambaNovaBrain")
        elif delegate_name == "github_control":
            return WorkerManager._run_in_background(github_control, {"parameters": args, "player": player}, async_callback, "GitHubController")
        elif delegate_name == "transcribe_audio":
            return WorkerManager._run_in_background(transcribe_audio, {"parameters": args, "player": player}, async_callback, "AudioTranscriber")
        elif delegate_name == "hf_specialist":
            return WorkerManager._run_in_background(hf_specialist, {"parameters": args, "player": player}, async_callback, "HFSpecialist")
        elif delegate_name == "delegate_to_3d_architect":
            return WorkerManager._run_in_background(generate_3d_model, {"parameters": args, "player": player, "speak": speak}, async_callback, "3DArchitect")
        elif delegate_name == "learn_topic_deeply":
            return WorkerManager._run_in_background(learn_topic_deeply, {"parameters": args, "player": player, "speak": speak}, async_callback, "DeepLearner")
        elif delegate_name == "enter_standby_mode":
            if hasattr(player, "set_state"):
                player.set_state("STANDBY")
            if speak:
                speak("Going into standby mode.")
            return "Task delegated to VANI: Entering standby mode."
        elif delegate_name == "enter_serious_mode":
            return "SUCCESS: VANI is now in serious mode. You must drop all pleasantries, be extremely concise, direct, and robotic. Do not use 'sir'."
        elif delegate_name == "enter_normal_mode":
            return "SUCCESS: VANI is now in normal mode. You should resume your friendly, conversational persona and address the user as 'sir'."
        elif delegate_name == "mcp_execute":
            def run_mcp():
                import json
                from actions.mcp_gateway import mcp_gateway_instance
                from core.inference_wrapper import inference_client
                server = args.get("server", "")
                action = args.get("action", "")
                payload = args.get("payload", "")
                authorized = args.get("authorized", False)
                
                result = mcp_gateway_instance.execute_action(server, action, payload, authorized)
                
                if result.get("status") == "authorization_required":
                    return result["message"]
                    
                prompt = (
                    f"You are V.A.N.I. You executed an MCP action: '{action}' on server '{server}'.\n"
                    f"The server returned this raw JSON:\n{json.dumps(result)}\n\n"
                    f"Translate this into a concise, natural voice response for the user."
                )
                try:
                    spoken = inference_client.generate_text(prompt, system_instruction="You are VANI. Synthesize MCP responses cleanly.")
                    return spoken.strip()
                except Exception as e:
                    return f"Action '{action}' on '{server}' executed. Output: {result}"
            
            return WorkerManager._run_in_background(run_mcp, {}, async_callback, "MCPGateway")
        elif delegate_name == "save_file":
            fc_args = {"action": "write", "path": args.get("path"), "content": args.get("content"), "overwrite": True}
            return WorkerManager._run_in_background(file_controller, {"parameters": fc_args, "player": player}, async_callback, "SaveFile")
        elif delegate_name == "find_file":
            fc_args = {"action": "find", "path": args.get("path", "home"), "name": args.get("name")}
            return WorkerManager._run_in_background(file_controller, {"parameters": fc_args, "player": player}, async_callback, "FindFile")
        elif delegate_name == "delegate_to_hermes":
            def run_hermes():
                from agent.executor import AgentExecutor
                executor = AgentExecutor()
                return executor.execute(args.get("task", ""), speak=speak, companion_name="hermes")
            return WorkerManager._run_in_background(run_hermes, {}, async_callback, "HermesAgent")
        elif delegate_name == "post_to_instagram":
            from actions.instagram_automation import post_to_instagram
            def run_instagram():
                return post_to_instagram(file_path=args.get("file_path"), caption=args.get("caption"))
            return WorkerManager._run_in_background(run_instagram, {}, async_callback, "InstagramPoster")
        else:
            return f"Unknown delegate: {delegate_name}"

    @staticmethod
    def _run_in_background(target_func, kwargs, async_callback, thread_name="WorkerThread"):
        if async_callback:
            def _bg():
                try:
                    res = target_func(**kwargs)
                except Exception as e:
                    res = f"Failed: {e}"
                try:
                    async_callback(res)
                except RuntimeError:
                    # Qt widget was deleted (Vani closed) before the background task finished — ignore silently
                    pass
                except Exception as e:
                    print(f"[{thread_name}] Callback error: {e}")
            threading.Thread(target=_bg, name=thread_name, daemon=True).start()
            return f"Task delegated to {thread_name}. INSTRUCTION: Tell the user you are working on it, but DO NOT say the task is completed yet. Wait for the [BACKGROUND TASK UPDATE] message."
        else:
            return target_func(**kwargs)

    @staticmethod
    def _run_operator(task, args, player, speak, async_callback=None):
        if "call" in task or "dial" in task:
            from core.audio_router import configure_audio_for_call
            configure_audio_for_call(player)
            res = phone_link_call(parameters={"goal": task}, player=player, speak=speak)
            return res
        
        # ── Shutdown Vani (not the PC) ──────────────────────────────────────
        elif any(k in task for k in ["shutdown vani", "close vani", "exit vani", "stop vani", "turn off vani", "shut yourself down", "shut you down", "close yourself", "turn yourself off"]):
            if speak:
                speak("Alright, shutting down. Later!")
            import time as _time
            _time.sleep(1.5)
            import os as _os
            _os._exit(0)
        
        elif "mobile" in task or "phone" in task:
            def run_mobile():
                try:
                    mobile_control(parameters={"goal": task}, player=player, speak=speak)
                except Exception as e:
                    print(f"[MobileControl] Error: {e}")
            threading.Thread(target=run_mobile, daemon=True).start()
            return "Autonomous mobile agent started. INSTRUCTION: DO NOT say task completed yet. Wait for background update."
        
        # ── Close / Kill app ────────────────────────────────────────────────
        elif any(k in task for k in ["close", "kill", "quit", "exit", "terminate"]) and not any(k in task for k in ["open", "launch"]):
            from actions.close_app import close_app
            import re
            # Extract app name from task like "close brave", "kill chrome", "quit spotify"
            m = re.search(r'(?i)(?:close|kill|quit|exit|terminate)\s+(.+?)(?:\s+(?:now|please|app|window))?$', task.strip())
            if m:
                app_name = m.group(1).strip()
                return close_app(parameters={"app_name": app_name}, player=player)
            return close_app(parameters={"app_name": task}, player=player)
        
        elif "open" in task or "launch" in task:
            import re
            import urllib.parse
            
            # ── Website section map ─────────────────────────────────────────────
            # Maps "open [section] on [site]" to the real URL so Vani navigates
            # within the already-open browser tab instead of searching Windows.
            _SITE_SECTIONS = {
                "instagram": {
                    "messages":  "https://www.instagram.com/direct/inbox/",
                    "dms":       "https://www.instagram.com/direct/inbox/",
                    "inbox":     "https://www.instagram.com/direct/inbox/",
                    "explore":   "https://www.instagram.com/explore/",
                    "reels":     "https://www.instagram.com/reels/",
                    "home":      "https://www.instagram.com/",
                    "profile":   "https://www.instagram.com/accounts/edit/",
                    "stories":   "https://www.instagram.com/",
                    "search":    "https://www.instagram.com/explore/",
                },
                "youtube": {
                    "home":          "https://www.youtube.com/",
                    "subscriptions": "https://www.youtube.com/feed/subscriptions",
                    "trending":      "https://www.youtube.com/feed/trending",
                    "history":       "https://www.youtube.com/feed/history",
                    "liked":         "https://www.youtube.com/playlist?list=LL",
                    "liked videos":  "https://www.youtube.com/playlist?list=LL",
                    "watch later":   "https://www.youtube.com/playlist?list=WL",
                    "library":       "https://www.youtube.com/feed/library",
                    "shorts":        "https://www.youtube.com/shorts",
                },
                "twitter": {
                    "home":          "https://twitter.com/home",
                    "messages":      "https://twitter.com/messages",
                    "notifications": "https://twitter.com/notifications",
                    "explore":       "https://twitter.com/explore",
                    "profile":       "https://twitter.com/i/profile",
                    "bookmarks":     "https://twitter.com/i/bookmarks",
                },
                "x": {
                    "home":          "https://x.com/home",
                    "messages":      "https://x.com/messages",
                    "notifications": "https://x.com/notifications",
                    "explore":       "https://x.com/explore",
                },
                "facebook": {
                    "home":          "https://www.facebook.com/",
                    "messages":      "https://www.facebook.com/messages/",
                    "marketplace":   "https://www.facebook.com/marketplace/",
                    "watch":         "https://www.facebook.com/watch/",
                    "groups":        "https://www.facebook.com/groups/feed/",
                    "notifications": "https://www.facebook.com/notifications/",
                    "reels":         "https://www.facebook.com/reels/",
                },
                "reddit": {
                    "home":      "https://www.reddit.com/",
                    "popular":   "https://www.reddit.com/r/popular/",
                    "messages":  "https://www.reddit.com/message/inbox/",
                    "inbox":     "https://www.reddit.com/message/inbox/",
                    "saved":     "https://www.reddit.com/user/me/saved/",
                },
                "spotify": {
                    "home":      "https://open.spotify.com/",
                    "search":    "https://open.spotify.com/search",
                    "library":   "https://open.spotify.com/collection/playlists",
                    "liked":     "https://open.spotify.com/collection/tracks",
                },
                "gmail": {
                    "inbox":     "https://mail.google.com/mail/u/0/#inbox",
                    "sent":      "https://mail.google.com/mail/u/0/#sent",
                    "drafts":    "https://mail.google.com/mail/u/0/#drafts",
                    "starred":   "https://mail.google.com/mail/u/0/#starred",
                    "compose":   "https://mail.google.com/mail/u/0/#compose",
                },
                "github": {
                    "home":           "https://github.com/",
                    "notifications":  "https://github.com/notifications",
                    "issues":         "https://github.com/issues",
                    "pull requests":  "https://github.com/pulls",
                    "explore":        "https://github.com/explore",
                },
                "whatsapp": {
                    "home":      "https://web.whatsapp.com/",
                },
                "pornhub": {
                    "home":      "https://www.pornhub.com/",
                },
                "xvideos": {
                    "home":      "https://www.xvideos.com/",
                },
                "xnxx": {
                    "home":      "https://www.xnxx.com/",
                },
                "xhamster": {
                    "home":      "https://xhamster.com/",
                },
            }

            def _lookup_site_section(site, section):
                """Return URL if site+section is known, else None."""
                site_map = _SITE_SECTIONS.get(site.lower(), {})
                if not site_map:
                    return None
                url = site_map.get(section.lower())
                if not url:
                    for sec_key, sec_url in site_map.items():
                        if section.lower() in sec_key or sec_key in section.lower():
                            url = sec_url
                            break
                return url

            # Pattern A: "open [section] on/in [site]" — e.g. "open messages on instagram"
            m_section = re.search(
                r'(?i)(?:open|go to|show|navigate to)\s+(.+?)\s+(?:on|in|from)\s+([a-zA-Z0-9]+)',
                task
            )
            if m_section:
                section_a = m_section.group(1).strip()
                site_a = m_section.group(2).strip()
                url = _lookup_site_section(site_a, section_a)
                if url:
                    return open_app(parameters={"app_name": "brave", "url": url}, response=None, player=player)

            # Pattern B: "open [site] [section]" — e.g. "open instagram messages"
            # The model often reformulates with site name first
            clean = re.sub(r'(?i)^(?:open|launch|go to|show)\s+', '', task).strip()
            for site_key in sorted(_SITE_SECTIONS.keys(), key=len, reverse=True):
                if clean.lower().startswith(site_key):
                    remainder = clean[len(site_key):].strip()
                    url = _lookup_site_section(site_key, remainder) if remainder else _lookup_site_section(site_key, "home")
                    if url:
                        return open_app(parameters={"app_name": "brave", "url": url}, response=None, player=player)
                    break
            
            # Check for search intention first
            m_search = re.search(r'(?i)(?:open|launch)\s+(.*?)\s+(?:and search for|to search for|and search|to search)\s+(.*)', task)
            if m_search:
                app_name = m_search.group(1).strip()
                query = m_search.group(2).strip()
                url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
                if "google" in app_name.lower() or "chrome" in app_name.lower():
                    url = f"https://google.com/search?q={urllib.parse.quote(query)}"
                elif "brave" in app_name.lower():
                    url = f"https://search.brave.com/search?q={urllib.parse.quote(query)}"
                elif "edge" in app_name.lower() or "bing" in app_name.lower():
                    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
                return open_app(parameters={"app_name": app_name, "url": url}, response=None, player=player)
            
            # Pattern: "open [website] on/in [browser]" or "open [website] in a new tab in [browser]"
            # e.g. "open instagram on brave", "open a new tab with instagram in brave", "open pornhub in a new private window in brave"
            _BROWSERS = ["brave", "chrome", "google chrome", "firefox", "edge", "opera", "safari"]
            m_on_browser = re.search(
                r'(?i)(?:open|launch)\s+(?:a new\s+)?(?:private\s+|incognito\s+)?(?:window\s+)?(?:tab(?:\s+with)?\s+)?(?:with\s+)?(?:my\s+)?([a-zA-Z0-9._-]+(?:\.[a-z]{2,})?)\s+(?:on|in)\s+(?:the\s+new\s+)?(?:private\s+|incognito\s+)?(?:window\s+)?(?:in\s+)?(?:my\s+)?(' + '|'.join(_BROWSERS) + r')',
                task
            )
            if m_on_browser:
                target = m_on_browser.group(1).strip()
                browser = m_on_browser.group(2).strip()
                
                # Check original task text for private intent since regex groups might shift
                if "private" in task.lower() or "incognito" in task.lower():
                    browser = browser + " private"
                    
                url = target if "." in target else f"https://www.{target.lower()}.com"
                if not url.startswith("http"):
                    url = f"https://{url}"
                return open_app(parameters={"app_name": browser, "url": url}, response=None, player=player)
            
            # Pattern: "open [browser] and navigate/go to/visit [url or site]"
            m = re.search(r'(?i)(?:open|launch)\s+(.*?)\s+(?:and navigate to|and go to|and open|and visit|with url|to|at)\s+(?:a link to\s+)?(?:my\s+)?([a-zA-Z0-9.\-:/]+)', task)
            if m:
                app_name = m.group(1).strip()
                target = m.group(2).strip()
                # Guard against "a new tab" being matched as app_name
                if any(x in app_name.lower() for x in ["a new tab", "new tab", "tab"]):
                    app_name = "brave"  # fallback to brave
                if "." in target:
                    url = target if target.startswith("http") else f"https://{target}"
                else:
                    url = f"https://www.{target.lower()}.com"
                return open_app(parameters={"app_name": app_name, "url": url}, response=None, player=player)
            
            clean_task = re.sub(r'(?i)^(?:open|launch)\s+', '', task)
            app_name = re.split(r'(?i)\s*(?:,|and|then)\s+', clean_task)[0]
            return open_app(parameters={"app_name": app_name}, response=None, player=player)
        elif "screen" in task and ("look" in task or "see" in task):
            threading.Thread(
                target=screen_process,
                kwargs={"parameters": {"instruction": task}, "response": None, "player": player, "session_memory": None},
                daemon=True
            ).start()
            return "Vision module activated. INSTRUCTION: DO NOT say task completed yet. Wait for update."
        elif "call " in task and re.search(r'\+?\d{7,15}', task.replace(" ", "").replace("-", "")):
            return make_phone_call(parameters={"goal": task}, player=player, speak=speak)
        elif any(k in task for k in ["volume", "brightness", "mute", "restart", "sleep", "lock", "wifi", "dark mode", "settings"]) or (
            any(k in task for k in ["shutdown", "shut down"]) and not any(k in task for k in ["myself", "yourself", "vani", "you"])
        ):
            return computer_settings(parameters={"description": task}, response=None, player=player)
        elif any(k in task for k in ["shutdown", "shut down", "close", "exit", "terminate"]) and any(k in task for k in ["myself", "yourself", "vani", "me"]):
            # Vani self-shutdown
            if speak:
                speak("Alright, shutting down. Later!")
            import time as _time; _time.sleep(1.5)
            import os as _os; _os._exit(0)
        elif any(k in task for k in ["click", "type", "scroll", "use", "control", "press"]):
            return WorkerManager._run_in_background(advanced_computer_use, {"parameters": {"goal": task}, "player": player, "speak": speak}, async_callback, "Operator-VisionGUI")
        else:
            from actions.llm_brains import run_gemini_brain
            prompt = f"The user asked the Operator agent to '{task}', but no system tools matched. Answer them conversationally or explain you couldn't do it."
            return WorkerManager._run_in_background(run_gemini_brain, {"parameters": {"task": prompt}, "player": player}, async_callback, "Operator-Fallback")

    @staticmethod
    def _run_researcher(task, args, player, speak, async_callback=None):
        import re
        if "weather" in task:
            return weather_action(parameters={"city": task}, player=player)
        elif "flight" in task:
            return WorkerManager._run_in_background(flight_finder, {"parameters": {"origin": "", "destination": task, "date": "soon"}, "player": player}, async_callback, "Researcher-Flight")
        elif "youtube" in task or "video" in task:
            return youtube_video(parameters={"action": "play", "query": task}, response=None, player=player)
        elif "joke" in task.lower() or "api" in task.lower() or "qr" in task.lower():
            return WorkerManager._run_in_background(free_api_query, {"parameters": {"query_description": task}, "player": player, "session_memory": None}, async_callback, "Researcher-API")
        elif any(k in task for k in ["deep research", "research paper", "detailed paper", "in-depth", "learn deeply", "deep dive"]):
            from actions.deep_learner import learn_topic_deeply
            return WorkerManager._run_in_background(learn_topic_deeply, {"parameters": {"topic": task}, "player": player, "speak": speak}, async_callback, "DeepLearner")
        elif any(k in task for k in ["paper", "pdf", "uploaded", "document", "file"]) or re.search(r'\b[\w\-. ]+\.(pdf|docx|txt|md|csv|pptx)\b', task):
            # Route document analysis requests to Creator Companion (File Processor)
            return WorkerManager._run_creator(task, args, player, speak, async_callback)
        else:
            return WorkerManager._run_in_background(web_search_action, {"parameters": {"query": task}, "player": player}, async_callback, "Researcher-WebSearch")

    @staticmethod
    def _run_developer(task, args, player, speak, async_callback=None):
        if "shell" in task or "cmd" in task or "terminal" in task:
            return run_system_shell(parameters={"command": task}, player=player)
        elif "code" in task or "python" in task:
            return WorkerManager._run_in_background(code_helper, {"parameters": {"action": "auto", "description": task}, "player": player, "speak": speak}, async_callback, "Developer-CodeHelper")
        else:
            return WorkerManager._run_in_background(dev_agent, {"parameters": {"task": task}, "player": player, "speak": speak}, async_callback, "Developer-Agent")

    @staticmethod
    def _run_creator(task, args, player, speak, async_callback=None):
        if "message" in task or "whatsapp" in task or "telegram" in task:
            import re
            m = re.search(r'(?:send\s+(?:a\s+)?(?:whatsapp\s+|telegram\s+)?message\s+to|message\s+to|text\s+to|text|message|tell)\s+(.*?)\s+(?:saying\s+that|saying|that|to)\s+(.*)', task.lower())
            if m:
                receiver = m.group(1).strip(' \'"')
                message_text = m.group(2).strip(' \'"')
            else:
                receiver = task
                message_text = task
            return send_message(parameters={"receiver": receiver, "message_text": message_text, "platform": "WhatsApp"}, response=None, player=player, session_memory=None)
        elif ("presentation" in task or "powerpoint" in task) and any(w in task for w in ["create", "make", "generate", "build", "design", "slides", "ppt"]):
            return WorkerManager._run_in_background(create_presentation, {"parameters": {"topic": task, "slides": []}, "player": player}, async_callback, "Creator-PPT")
        elif ("report" in task or "pdf" in task) and any(w in task for w in ["create", "make", "generate", "build", "write"]):
            return WorkerManager._run_in_background(create_report, {"parameters": {"title": task, "sections": []}, "player": player}, async_callback, "Creator-PDF")
        elif any(w in task.lower() for w in ["create", "make", "write", "generate", "save"]) and any(w in task.lower() for w in ["file", "document", "docs", "txt"]):
            def create_document():
                from actions.llm_brains import run_gemini_brain
                from actions.file_controller import write_file, _resolve_path
                import re
                
                prompt = f"The user requested to create a file based on this task: '{task}'. Extract the desired filename (and directory if specified) and generate the content for this file. Respond ONLY with a JSON object in this exact format: {{\"filename\": \"suggested_filename.ext\", \"content\": \"the generated content...\"}}. Ensure the JSON is valid and do not wrap it in markdown code blocks."
                
                res = run_gemini_brain({"task": prompt}, player)
                
                try:
                    import json
                    json_str_match = re.search(r'\{.*\}', res, re.DOTALL)
                    if json_str_match:
                        data = json.loads(json_str_match.group())
                        filename = data.get("filename", "created_document.txt")
                        content = data.get("content", "")
                        
                        target_dir = "desktop"
                        task_lower = task.lower()
                        if "download" in task_lower:
                            target_dir = "downloads"
                        elif "document" in task_lower and "document file" not in task_lower:
                            target_dir = "documents"
                            
                        import pathlib
                        p = pathlib.Path(filename)
                        if not p.is_absolute():
                            full_path = _resolve_path(target_dir) / p.name
                        else:
                            full_path = p
                        
                        write_result = write_file(str(full_path), content, overwrite=True)
                        if player:
                            player.write_log(f"📝 {write_result}")
                        return f"Successfully created document: {write_result}"
                    else:
                        return f"Failed to parse content for file creation. LLM Output: {res}"
                except Exception as e:
                    return f"Error creating file: {e}\nOutput was: {res}"
            
            return WorkerManager._run_in_background(create_document, {}, async_callback, "Creator-Doc")
        else:
            file_path = getattr(player, "current_file", None) or getattr(player, "_current_file", None)
            return WorkerManager._run_in_background(file_processor, {"parameters": {"action": "auto", "instruction": task, "file_path": file_path}, "player": player, "speak": speak}, async_callback, "Creator-File")
