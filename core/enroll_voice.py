import os
import time
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from core.biometrics import voice_biometrics

def enroll_voice():
    duration = 10  # seconds
    fs = 16000
    
    print("="*50)
    print("🎙️  VOICE BIOMETRICS ENROLLMENT  🎙️")
    print("="*50)
    print("Please read the following text aloud when the recording starts:")
    print("\n\"Hello Jarvis. I am the authorized user of this system.")
    print("Please verify my voice and grant me full access to all commands.")
    print("This is my voice profile recording.\"\n")
    
    input("Press Enter to start recording...")
    
    print(f"\n🔴 Recording for {duration} seconds... Please speak now.")
    
    # Record audio
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    
    print("✅ Recording finished. Processing and extracting voice embedding...")
    
    temp_wav = Path(__file__).resolve().parent.parent / "config" / "temp_enroll.wav"
    temp_wav.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to temp file
    sf.write(str(temp_wav), recording, fs)
    
    try:
        # Enroll using biometrics
        success = voice_biometrics.enroll(str(temp_wav))
        if success:
            print(f"\n🎉 Success! Your voice profile has been securely saved.")
            print(f"Profile saved to: {voice_biometrics.profile_path}")
            print("Jarvis will now only respond to this voice.")
        else:
            print("\n❌ Failed to extract voice embedding.")
    except Exception as e:
        print(f"\n❌ Error during enrollment: {e}")
    finally:
        # Clean up
        if temp_wav.exists():
            os.remove(temp_wav)

if __name__ == "__main__":
    enroll_voice()
