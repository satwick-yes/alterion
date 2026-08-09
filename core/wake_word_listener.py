import time
import comtypes.client
import subprocess
import sys
import os

def start_wake_word():
    try:
        recognizer = comtypes.client.CreateObject("SAPI.SpSharedRecognizer")
        context = recognizer.CreateRecoContext()
        grammar = context.CreateGrammar(1)
        grammar.DictationSetState(0) # Disable dictation

        rule = grammar.Rules.Add("WakeWordRule", 33, 1) # 33 is arbitrary ID, 1 is TopLevel
        rule.InitialState.AddWordTransition(None, "wake up vani")
        rule.InitialState.AddWordTransition(None, "vani")
        grammar.Rules.Commit()
        grammar.CmdSetRuleState("WakeWordRule", 1) # 1 = Active
        
        def OnRecognition(StreamNumber, StreamPosition, RecognitionType, Result):
            phrase = Result.PhraseInfo.GetText()
            print("Recognized:", phrase)
            if phrase.lower() in ["wake up vani", "vani"]:
                print("Wake word detected! Launching Vani...")
                try:
                    import winsound
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
                except:
                    pass
                
                # Launch Vani
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                bat_path = os.path.join(base_dir, "Start_Vani.bat")
                
                if os.path.exists(bat_path):
                    # Launch the batch file in a new command window
                    subprocess.Popen(["cmd.exe", "/c", "start", '""', bat_path], cwd=base_dir, shell=True)
                else:
                    # Fallback to python main.py
                    subprocess.Popen(["python", "main.py"], cwd=base_dir, creationflags=subprocess.CREATE_NEW_CONSOLE)
                
                # Forcefully exit the listener script so it doesn't conflict
                os._exit(0)

        # Keep a reference to the event sink
        sink = comtypes.client.GetEvents(context, {"OnRecognition": OnRecognition})
        print("Listening for wake word 'wake up vani'...")
        
        # Keep script running
        while True:
            time.sleep(1)
            
    except Exception as e:
        print("SAPI error:", e)
        time.sleep(5)

if __name__ == "__main__":
    # Give a small delay in case Vani just closed, so we don't conflict with any cleanup
    time.sleep(2)
    start_wake_word()
