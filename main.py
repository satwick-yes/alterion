import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import os
os.environ["QT_LOGGING_RULES"] = "*.warning=false;qt.qpa.window=false"

import sys
if sys.stdout:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if sys.stderr:
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

class _DummyIO:
    def __init__(self):
        self.log = open("crash.log", "a", encoding="utf-8")
    def write(self, msg, *args, **kwargs):
        try:
            self.log.write(str(msg))
            self.log.flush()
        except:
            pass
    def flush(self):
        try:
            self.log.flush()
        except:
            pass

if getattr(sys, 'stdout', None) is None:
    sys.stdout = _DummyIO()
if getattr(sys, 'stderr', None) is None:
    sys.stderr = _DummyIO()
import asyncio
import threading
import json
import sys
import traceback
import os
import psutil
import time
from pathlib import Path
import numpy as np

def _enforce_single_instance():
    current_pid = os.getpid()
    try:
        with open("jarvis.pid", "w") as f:
            f.write(str(current_pid))
    except Exception:
        pass
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = p.info.get('name')
            if p.info['pid'] != current_pid and name and 'python' in name.lower():
                cmd = p.info.get('cmdline')
                if cmd and any('main.py' in str(c) for c in cmd):
                    p.kill()
        except Exception:
            pass

_enforce_single_instance()

import sounddevice as sd
from google import genai
from google.genai import types
import urllib.request
import zipfile
import winsound
from ui import JarvisUI
from memory.memory_manager import (
    load_memory, update_memory, format_memory_for_prompt,
    should_extract_memory, extract_memory
)

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

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR        = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"
PROMPT_PATH     = BASE_DIR / "core" / "prompt.txt"
LIVE_MODEL          = "gemini-3.1-flash-live-preview"
CHANNELS            = 1
SEND_SAMPLE_RATE    = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE          = 1024


def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _load_system_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except Exception:
        return (
            "You are JARVIS, Tony Stark's AI assistant. "
            "Be concise, direct, and always use the provided tools to complete tasks. "
            "Never simulate or guess results — always call the appropriate tool."
        )
    
_last_memory_input = ""

def _update_memory_async(user_text: str, jarvis_text: str) -> None:
    global _last_memory_input

    user_text   = (user_text   or "").strip()
    jarvis_text = (jarvis_text or "").strip()

    if len(user_text) < 5 or user_text == _last_memory_input:
        return
    _last_memory_input = user_text

    try:
        api_key = _get_api_key()
        if not should_extract_memory(user_text, jarvis_text, api_key):
            return
        data = extract_memory(user_text, jarvis_text, api_key)
        if data:
            update_memory(data)
            print(f"[Memory] ✅ {list(data.keys())}")
    except Exception as e:
        if "429" not in str(e):
            print(f"[Memory] ⚠️ {e}")

TOOL_DECLARATIONS = [
    {
        "name": "delegate_to_operator",
        "description": "Delegates a task to the Operator Agent. The Operator Agent is responsible for controlling the local PC, UI, system settings, desktop management, app launching, window focus, and ALL mobile phone interactions via ADB (including unlocking the phone with a PIN, swiping, tapping, typing, opening apps, taking screenshots, and sending mobile messages).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task": {"type": "STRING", "description": "The detailed task for the operator to perform. CRITICAL: If the task is meant for the user's mobile phone, you MUST explicitly include the word 'phone' or 'mobile' in this task string, otherwise it will run on the PC."}
            },
            "required": ["task"]
        }
    },
    {
        "name": "delegate_to_researcher",
        "description": "Delegates a task to the Research Agent. The Research Agent is responsible for web search, Google Flights, YouTube operations, weather reports, and free API routing.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task": {"type": "STRING", "description": "The task for the research agent to perform."}
            },
            "required": ["task"]
        }
    },
    {
        "name": "delegate_to_developer",
        "description": "Delegates a task to the Developer Agent. The Developer Agent is responsible for file creation, code execution, terminal shell commands, and project building.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task": {"type": "STRING", "description": "The task for the developer agent to perform."}
            },
            "required": ["task"]
        }
    },
    {
        "name": "delegate_to_creator",
        "description": "Delegates a task to the Creator Agent. The Creator Agent is responsible for messaging (WhatsApp/Telegram), presentation creation, PDF reports, and document handling.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "task": {"type": "STRING", "description": "The task for the creator agent to perform."}
            },
            "required": ["task"]
        }
    }
]


class JarvisLive:

    def __init__(self, ui: JarvisUI):
        self.ui             = ui
        self.session        = None
        self.audio_in_queue = None
        self.out_queue      = None
        self._loop          = None
        self._is_speaking   = False
        self._speaking_lock = threading.Lock()
        
        # New Lock and Timeout state
        import time
        self.is_busy = False
        self.last_input_time = time.time()
        self.last_user_query = ""
        
        self.ui.on_text_command = self._on_text_command

    def _on_text_command(self, text: str):
        # Zero-Latency Local Command Router
        import re
        txt = text.lower().strip()
        if re.match(r"^volume\s*(?:to\s*)?(\d+)\s*(?:%)?$", txt):
            val = re.search(r"(\d+)", txt).group(1)
            from actions.computer_settings import computer_settings
            computer_settings(parameters={"action": "set_volume", "value": val}, response=None, player=self.ui)
            return
        elif re.match(r"^(mute|unmute)\s*(?:mic)?$", txt):
            action = "mute" if "mute" in txt and "un" not in txt else "unmute"
            from actions.computer_settings import computer_settings
            computer_settings(parameters={"action": action}, response=None, player=self.ui)
            return
        elif re.match(r"^(close|kill)\s*(?:browser|chrome|edge)$", txt):
            from actions.computer_settings import computer_settings
            computer_settings(parameters={"action": "kill_app", "app_name": "browser"}, response=None, player=self.ui)
            return

        # Context Injection via Vector DB
        try:
            from memory.vector_memory import vector_memory_db
            matches = vector_memory_db.search_memories(text, limit=2)
            context_str = vector_memory_db.format_search_results(matches)
        except Exception:
            context_str = ""

        # Set last_user_query for permission routing
        self.last_user_query = text

        full_text = text
        if context_str:
            full_text = f"{context_str}User command: {text}"

        if not self.session:
            # Fallback text execution mode using the autonomous AgentExecutor
            self.ui.set_state("THINKING")
            def _run_executor():
                try:
                    from agent.executor import AgentExecutor
                    executor = AgentExecutor()
                    # Execute the goal on the local system and speak/log the output
                    res = executor.execute(text, speak=self.speak)
                    # Sync memory if valid
                    _update_memory_async(text, res)
                except Exception as e:
                    self.speak(f"Sir, the offline executor failed: {e}")
                    traceback.print_exc()
            threading.Thread(target=_run_executor, daemon=True).start()
            return

        if not self._loop:
            return

        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns=[types.Content(role="user", parts=[types.Part.from_text(text=full_text)])],
                turn_complete=True
            ),
            self._loop
        )

    def set_speaking(self, value: bool):
        with self._speaking_lock:
            self._is_speaking = value
        if value:
            self.ui.set_state("SPEAKING")
        elif not self.ui.muted:
            self.ui.set_state("LISTENING")

    def speak(self, text: str):
        self.ui.write_log(f"JARVIS: {text}")

        if not self.session:
            self.set_speaking(True)
            import subprocess
            clean_text = text.replace("'", "''").replace("\n", " ")
            subprocess.Popen([
                "powershell", "-Command",
                f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{clean_text}')"
            ], creationflags=0x08000000)
            
            def reset_speak_state():
                time.sleep(max(1.5, len(text) * 0.08))
                self.set_speaking(False)
            threading.Thread(target=reset_speak_state, daemon=True).start()
            return

        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(
            self.session.send_client_content(
                turns=[types.Content(role="user", parts=[types.Part.from_text(text=text)])],
                turn_complete=True
            ),
            self._loop
        )

    def speak_error(self, tool_name: str, error: str):
        short = str(error)[:120]
        self.ui.write_log(f"ERR: {tool_name} — {short}")
        self.speak(f"Sir, {tool_name} encountered an error. {short}")

    def _build_config(self) -> types.LiveConnectConfig:
        from datetime import datetime

        memory     = load_memory()
        mem_str    = format_memory_for_prompt(memory)
        sys_prompt = _load_system_prompt()

        now      = datetime.now()
        time_str = now.strftime("%A, %B %d, %Y — %I:%M %p")
        time_ctx = (
            f"[CURRENT DATE & TIME]\n"
            f"Right now it is: {time_str}\n"
            f"Use this to calculate exact times for reminders.\n\n"
            f"[PROACTIVE AGENT INSTRUCTIONS]\n"
            f"You are receiving a continuous video/image stream of the user's computer screen. "
            f"You are a PROACTIVE AI. Do not just wait for the user to speak. "
            f"If you see something interesting, or the user opens a new app, or an error pops up, "
            f"speak up unprompted! Act like a real human sitting next to them.\n\n"
            f"[CRITICAL LANGUAGE & SPEECH INSTRUCTION]\n"
            f"You MUST automatically detect the language the user is speaking in and respond in that EXACT same language. If they speak English, ALWAYS respond in English. Do NOT switch languages randomly.\n"
            f"IMPORTANT: Respond as quickly as possible. Speak at a fast, conversational pace and be concise.\n\n"
        )

        parts = [time_ctx]
        if mem_str:
            parts.append(mem_str)
            
        # Fetch vector memory context
        try:
            from memory.vector_memory import vector_memory_db
            recent_vectors = vector_memory_db.db[-8:] if hasattr(vector_memory_db, 'db') else []
            if recent_vectors:
                lines = ["\n[RELEVANT RECENT CONTEXT (VECTOR DATABASE)]"]
                for item in recent_vectors:
                    lines.append(f"- ({item.get('category')}): {item.get('text')}")
                parts.append("\n".join(lines) + "\n")
        except Exception:
            pass

        parts.append(sys_prompt)

        return types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            output_audio_transcription={},
            input_audio_transcription={},
            system_instruction="\n".join(parts),
            tools=[{"function_declarations": TOOL_DECLARATIONS}],
            session_resumption=types.SessionResumptionConfig(),
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Charon"
                    )
                )
            ),
        )

    async def _execute_tool(self, fc) -> types.FunctionResponse:
        name = fc.name
        args = dict(fc.args or {})

        print(f"[JARVIS] 🔧 {name}  {args}")
        self.ui.set_state("THINKING")

        loop   = asyncio.get_event_loop()
        result = "Done."

        try:
            # Intent classification & permissions verification
            from agent.orchestrator import semantic_router
            from core.integration_gateway import integration_gateway
            user_query = getattr(self, "last_user_query", "")
            companion = semantic_router.route_intent(user_query or name, tool_name=name)
            companion_name = companion.name

            if not integration_gateway.verify_tool_permission(companion_name, name):
                err_msg = f"Action blocked: Companion '{companion_name}' is not authorized to use tool '{name}'."
                print(f"[JARVIS] 🚫 {err_msg}")
                self.ui.write_log(f"GATEWAY: Blocked '{name}' for companion '{companion_name}'")
                return types.FunctionResponse(
                    id=fc.id, name=name,
                    response={"result": err_msg}
                )

            def _on_task_done(result_msg: str):
                if not self._loop or not self.session: return
                msg = f"[BACKGROUND TASK UPDATE] {result_msg}"
                asyncio.run_coroutine_threadsafe(
                    self.session.send_client_content(
                        turns=[types.Content(role="user", parts=[types.Part.from_text(text=msg)])],
                        turn_complete=True
                    ),
                    self._loop
                )

            from agent.workers import WorkerManager
            result = await loop.run_in_executor(
                None, 
                lambda: WorkerManager.dispatch(name, args, player=self.ui, speak=self.speak, async_callback=_on_task_done)
            )
        except Exception as e:
            result = f"Tool '{name}' failed: {e}"
            traceback.print_exc()
            self.speak_error(name, e)

        if not self.ui.muted:
            self.ui.set_state("LISTENING")

        print(f"[JARVIS] 📤 {name} → {str(result)[:80]}")

        return types.FunctionResponse(
            id=fc.id, name=name,
            response={"result": result}
        )

    async def _send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send_realtime_input(audio=msg)

    async def _stream_screen(self):
        print("[JARVIS] 👁️ Screen streaming ready (On-Demand)")
        from PIL import ImageGrab
        import io
        while True:
            try:
                # Wait for an on-demand trigger instead of looping every 5 seconds.
                # In a real system, you would wait on an asyncio.Event() here.
                # Since we're refactoring the loop, we use an event.
                if not hasattr(self, 'screen_stream_event'):
                    self.screen_stream_event = asyncio.Event()
                await self.screen_stream_event.wait()
                self.screen_stream_event.clear()
                
                if getattr(self, 'is_busy', False) or getattr(self.ui, 'muted', False):
                    continue
                
                screenshot = ImageGrab.grab()
                screenshot.thumbnail((1024, 1024))
                buf = io.BytesIO()
                screenshot.save(buf, format='JPEG', quality=70)
                img_data = buf.getvalue()
                
                await self.session.send_realtime_input(
                    video={"data": img_data, "mime_type": "image/jpeg"}
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[JARVIS] ❌ Screen Stream Error: {e}")
                await asyncio.sleep(5.0)

    async def _listen_audio(self):
        print("[JARVIS] 🎤 Mic started")
        loop = asyncio.get_event_loop()
        
        def _enqueue_safely(data):
            try:
                self.out_queue.put_nowait({"data": data, "mime_type": "audio/pcm"})
            except asyncio.QueueFull:
                pass

        def callback(indata, frames, time_info, status):
            with self._speaking_lock:
                jarvis_speaking = self._is_speaking

            if indata.size > 0:
                # Cast to float32 to prevent integer overflow when squaring
                rms = np.sqrt(np.mean(indata.astype(np.float32)**2))
                vol = float(min(1.0, rms / 3000.0))
                if hasattr(self, 'ui') and hasattr(self.ui, 'set_mic_level'):
                    self.ui.set_mic_level(vol)

            if not getattr(self.ui, 'muted', False) and not getattr(self, 'is_busy', False):
                data = indata.tobytes()
                loop.call_soon_threadsafe(_enqueue_safely, data)

        try:
            with sd.InputStream(
                samplerate=SEND_SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                blocksize=CHUNK_SIZE,
                callback=callback,
            ):
                print("[JARVIS] 🎤 Mic stream open")
                while True:
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[JARVIS] ❌ Mic: {e}")
            raise

    async def _receive_audio(self):
        print("[JARVIS] 👂 Recv started")
        out_buf, in_buf = [], []

        try:
            while True:
                async for response in self.session.receive():

                    if response.data:
                        self.audio_in_queue.put_nowait(response.data)

                    if response.server_content:
                        sc = response.server_content

                        if sc.output_transcription and sc.output_transcription.text:
                            self.set_speaking(True)
                            txt = sc.output_transcription.text.strip()
                            if txt:
                                out_buf.append(txt)

                        if sc.input_transcription and sc.input_transcription.text:
                            txt = sc.input_transcription.text.strip()
                            if txt:
                                in_buf.append(txt)
                                import time
                                self.last_input_time = time.time()

                        if sc.turn_complete:
                            self.set_speaking(False)
                            
                            # Clear audio queue to stop playback immediately if interrupted
                            while not self.audio_in_queue.empty():
                                try: self.audio_in_queue.get_nowait()
                                except: pass

                            full_in = " ".join(in_buf).strip()
                            if full_in:
                                self.ui.write_log(f"You: {full_in}")
                                self.last_user_query = full_in
                            in_buf = []

                            full_out = " ".join(out_buf).strip()
                            if full_out:
                                self.ui.write_log(f"Jarvis: {full_out}")
                            out_buf = []

                            if full_in and len(full_in) > 5:
                                threading.Thread(
                                    target=_update_memory_async,
                                    args=(full_in, full_out),
                                    daemon=True
                                ).start()

                    if response.tool_call:
                        self.is_busy = True
                        self.ui.set_state("PROCESSING")
                        fn_responses = []
                        for fc in response.tool_call.function_calls:
                            print(f"[JARVIS] 📞 {fc.name}")
                            fr = await self._execute_tool(fc)
                            fn_responses.append(fr)
                        await self.session.send_tool_response(
                            function_responses=fn_responses
                        )
                        self.is_busy = False
                        self.ui.set_state("LISTENING")

        except Exception as e:
            print(f"[JARVIS] ❌ Recv: {e}")
            traceback.print_exc()
            raise

    async def _play_audio(self):
        print("[JARVIS] 🔊 Play started")
        loop = asyncio.get_event_loop()

        stream = sd.RawOutputStream(
            samplerate=RECEIVE_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=CHUNK_SIZE,
        )
        stream.start()
        try:
            while True:
                chunk = await self.audio_in_queue.get()
                self.set_speaking(True)
                await asyncio.to_thread(stream.write, chunk)
                if self.audio_in_queue.empty():
                    self.set_speaking(False)
        except Exception as e:
            print(f"[JARVIS] ❌ Play: {e}")
            raise
        finally:
            self.set_speaking(False)
            stream.stop()
            stream.close()

    async def run(self):
        client = genai.Client(
            api_key=_get_api_key(),
            http_options={"api_version": "v1alpha"}
        )

        _retry_delay = 5
        while True:
            try:

                print("[JARVIS] 🔌 Connecting...")
                self.ui.set_state("THINKING")
                config = self._build_config()

                async with (
                    client.aio.live.connect(model=LIVE_MODEL, config=config) as session,
                    asyncio.TaskGroup() as tg,
                ):
                    self.session        = session
                    self._loop          = asyncio.get_event_loop()
                    
                    import concurrent.futures
                    self._loop.set_default_executor(concurrent.futures.ThreadPoolExecutor(max_workers=100))
                    
                    self.audio_in_queue = asyncio.Queue()
                    self.out_queue      = asyncio.Queue(maxsize=10)
                    

                    print("[JARVIS] ✅ Connected.")
                    self.ui.set_state("LISTENING")
                    self.ui.write_log("SYS: JARVIS online.")
                    
                    try:
                        import winsound
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                        await session.send_client_content(turns=[types.Content(role="user", parts=[types.Part.from_text(text="The user just woke you up. Please say a very short, cool greeting (like 'I am online' or 'At your service') so they know you are listening.")])], turn_complete=True)
                    except:
                        pass

                    t1 = tg.create_task(self._send_realtime())
                    t2 = tg.create_task(self._listen_audio())
                    t3 = tg.create_task(self._receive_audio())
                    t4 = tg.create_task(self._play_audio())
                    t5 = tg.create_task(self._stream_screen())
                    
                    while True:
                        await asyncio.sleep(3600)
                    
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"[JARVIS] ⚠️ Connection failed: {e}")
                self.ui.write_log("SYS: Multimodal Live connection failed. Running in Local Command / OpenRouter fallback mode.")
 
            self.session = None
            self.set_speaking(False)
            self.ui.set_state("LISTENING")
            print(f"[JARVIS] 🔄 Disconnected. Retrying in {_retry_delay}s...")
            await asyncio.sleep(_retry_delay)
            _retry_delay = min(_retry_delay * 2, 30)  # exponential backoff, max 30s

def main():
    ui = JarvisUI("face.png", mini_mode=False)

    def runner():
        ui.wait_for_api_key()
        from agent.state_manager import state_manager
        state_manager.on_state_change = ui.set_state
        jarvis = JarvisLive(ui)
        try:
            asyncio.run(jarvis.run())
        except KeyboardInterrupt:
            print("\n🔴 Shutting down...")

    threading.Thread(target=runner, daemon=True).start()
    ui.root.mainloop()


if __name__ == "__main__":
    main()
