import sounddevice as sd

def get_vb_cable_devices():
    """
    Finds the VB-Cable audio devices for input and output using sounddevice.
    Returns (input_device_index, output_device_index)
    """
    devices = sd.query_devices()
    input_idx = None
    output_idx = None
    
    for idx, device in enumerate(devices):
        name = device['name'].lower()
        hostapi_name = sd.query_hostapis(device['hostapi'])['name']
        
        # PortAudio's WDM-KS does not support blocking API which we need for RawOutputStream
        if "WDM-KS" in hostapi_name:
            continue
            
        if "cable output" in name or "vb-audio" in name or "cable" in name:
            if device['max_input_channels'] > 0 and input_idx is None:
                input_idx = idx
        if "cable input" in name or "vb-audio" in name or "cable" in name:
            if device['max_output_channels'] > 0 and output_idx is None:
                output_idx = idx
                
    return input_idx, output_idx

def configure_audio_for_call(player=None):
    """
    Configures the audio streams to use VB-Cable for output and WASAPI loopback for input.
    """
    in_idx, out_idx = get_vb_cable_devices()
    if out_idx is None:
        print("[AudioRouter] VB-Cable not found. Audio routing may not work automatically.")
        return False
        
    print(f"[AudioRouter] VB-Cable found! Input: {in_idx}, Output: {out_idx}")
    # In a full implementation, this function would update the player/Vani's active
    # audio stream to use out_idx for TTS and in_idx (or WASAPI loopback) for STT.
    return True

if __name__ == "__main__":
    print("Sounddevice devices:", get_vb_cable_devices())
