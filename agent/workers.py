import threading
from actions.file_processor import file_processor
from actions.flight_finder     import flight_finder
from actions.open_app          import open_app
from actions.weather_report    import weather_action
from actions.send_message      import send_message
from actions.reminder          import reminder
from actions.computer_settings import computer_settings
from actions.screen_processor  import screen_process
from actions.youtube_video     import youtube_video
from actions.desktop           import desktop_control
from actions.browser_control   import browser_control
from actions.file_controller   import file_controller
from actions.code_helper       import code_helper
from actions.dev_agent         import dev_agent
from actions.web_search        import web_search as web_search_action
from actions.computer_control  import computer_control
from actions.vision_computer_use import advanced_computer_use
from actions.game_updater      import game_updater
from actions.image_generator   import generate_image
from actions.presentation_maker import create_presentation
from actions.report_maker      import create_report
from actions.system_shell      import run_system_shell
from actions.free_apis_router  import free_api_query
from actions.mobile_control    import mobile_control
from actions.virtual_hand_control import virtual_hand_control
from actions.task_library import execute_hardcoded_task

class WorkerManager:
    @staticmethod
    def dispatch(delegate_name, args, player, speak, async_callback=None):
        print(f"[WorkerManager] Dispatching to {delegate_name} with args: {args}")
        task = args.get("task", "").lower()
        
        # Intercept hardcoded tasks first
        result = execute_hardcoded_task(task)
        if result:
            return result
            
        if delegate_name == "delegate_to_operator":
            return WorkerManager._run_operator(task, args, player, speak, async_callback)
        elif delegate_name == "delegate_to_researcher":
            return WorkerManager._run_researcher(task, args, player, speak, async_callback)
        elif delegate_name == "delegate_to_developer":
            return WorkerManager._run_developer(task, args, player, speak, async_callback)
        elif delegate_name == "delegate_to_creator":
            return WorkerManager._run_creator(task, args, player, speak, async_callback)
        else:
            return f"Unknown delegate: {delegate_name}"

    @staticmethod
    def _run_in_background(target_func, kwargs, async_callback, thread_name="WorkerThread"):
        if async_callback:
            def _bg():
                try:
                    res = target_func(**kwargs)
                    async_callback(res)
                except Exception as e:
                    async_callback(f"Failed: {e}")
            threading.Thread(target=_bg, name=thread_name, daemon=True).start()
            return f"Task delegated to {thread_name}."
        else:
            return target_func(**kwargs)

    @staticmethod
    def _run_operator(task, args, player, speak, async_callback=None):
        if "mobile" in task or "phone" in task:
            def run_mobile():
                try:
                    mobile_control(parameters={"goal": task}, player=player, speak=speak)
                except Exception as e:
                    print(f"[MobileControl] Error: {e}")
            threading.Thread(target=run_mobile, daemon=True).start()
            return "Autonomous mobile agent started."
        elif "open" in task or "launch" in task:
            import re
            m = re.search(r'(?i)(?:open|launch)\s+(.*?)\s+(?:and navigate to|and go to|and open|and visit|to|at)\s+(https?://[^\s]+|[\w.-]+\.[a-z]{2,})', task)
            if m:
                app_name = m.group(1).strip()
                url = m.group(2).strip()
                return open_app(parameters={"app_name": app_name, "url": url}, response=None, player=player)
            
            app_name = task.replace("open ", "").replace("launch ", "").replace("Open ", "").replace("Launch ", "")
            return open_app(parameters={"app_name": app_name}, response=None, player=player)
        elif "screen" in task and ("look" in task or "see" in task):
            threading.Thread(
                target=screen_process,
                kwargs={"parameters": {"instruction": task}, "response": None, "player": player, "session_memory": None},
                daemon=True
            ).start()
            return "Vision module activated."
        elif "volume" in task or "brightness" in task or "mute" in task:
            return computer_settings(parameters={"action": "volume_up", "description": task}, response=None, player=player)
        elif "click" in task or "type" in task or "scroll" in task:
            return advanced_computer_use(parameters={"goal": task}, player=player, speak=speak)
        else:
            return computer_settings(parameters={"action": "unknown", "description": task}, response=None, player=player)

    @staticmethod
    def _run_researcher(task, args, player, speak, async_callback=None):
        if "weather" in task:
            return weather_action(parameters={"city": task}, player=player)
        elif "flight" in task:
            return WorkerManager._run_in_background(flight_finder, {"parameters": {"origin": "", "destination": task, "date": "soon"}, "player": player}, async_callback, "Researcher-Flight")
        elif "youtube" in task or "video" in task:
            return youtube_video(parameters={"action": "play", "query": task}, response=None, player=player)
        elif "joke" in task or "api" in task:
            return WorkerManager._run_in_background(free_api_query, {"parameters": {"query_description": task}, "player": player, "session_memory": None}, async_callback, "Researcher-API")
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
            m = re.search(r'(?:send a message to|send message to|text|message|tell)\s+([\w\s]+?)\s+(?:saying that|saying|that|to)\s+(.*)', task.lower())
            if m:
                receiver = m.group(1).strip()
                message_text = m.group(2).strip()
            else:
                receiver = task
                message_text = task
            return send_message(parameters={"receiver": receiver, "message_text": message_text, "platform": "WhatsApp"}, response=None, player=player, session_memory=None)
        elif "presentation" in task or "powerpoint" in task:
            return WorkerManager._run_in_background(create_presentation, {"parameters": {"topic": task, "slides": []}, "player": player}, async_callback, "Creator-PPT")
        elif "report" in task or "pdf" in task:
            return WorkerManager._run_in_background(create_report, {"parameters": {"title": task, "sections": []}, "player": player}, async_callback, "Creator-PDF")
        else:
            return WorkerManager._run_in_background(file_processor, {"parameters": {"action": "summarize", "instruction": task, "file_path": getattr(player, "current_file", None)}, "player": player, "speak": speak}, async_callback, "Creator-File")
