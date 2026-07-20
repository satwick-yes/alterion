import os
import io
import torch
import numpy as np
import soundfile as sf
from pathlib import Path
import logging

logger = logging.getLogger("biometrics")

class VoiceBiometrics:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.profile_path = self.base_dir / "config" / "user_voice_profile.pt"
        self.model = None
        self.enrolled_embedding = None
        self.is_loaded = False
        
        # We don't load the model immediately to avoid blocking startup
        if self.profile_path.exists():
            try:
                self.enrolled_embedding = torch.load(self.profile_path)
            except Exception as e:
                logger.error(f"[VoiceBiometrics] Failed to load voice profile: {e}")

    def _load_model(self):
        if self.is_loaded:
            return
        logger.info("[VoiceBiometrics] Loading SpeechBrain ECAPA-TDNN model...")
        try:
            try:
                from speechbrain.inference.speaker import SpeakerRecognition
            except ImportError:
                # Fallback for speechbrain < 1.0
                from speechbrain.pretrained import SpeakerRecognition
                
            # Download and load the pre-trained model
            self.model = SpeakerRecognition.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb", 
                savedir=str(self.base_dir / "models" / "spkrec-ecapa-voxceleb"),
                run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
            )
            self.is_loaded = True
            logger.info("[VoiceBiometrics] Model loaded successfully.")
        except Exception as e:
            logger.error(f"[VoiceBiometrics] Failed to load model: {e}")
            raise

    def enroll(self, audio_file_path: str):
        """
        Extracts embedding from an audio file and saves it as the user profile.
        """
        self._load_model()
        logger.info(f"[VoiceBiometrics] Enrolling voice from {audio_file_path}...")
        
        # Extract embedding using SpeechBrain
        signal, fs = sf.read(audio_file_path)
        # Convert to mono if stereo
        if len(signal.shape) > 1:
            signal = signal.mean(axis=1)
            
        # Convert to tensor
        signal_tensor = torch.tensor(signal).float()
        
        # Resample if not 16000Hz (SpeechBrain default)
        if fs != 16000:
            import torchaudio.transforms as T
            resampler = T.Resample(fs, 16000)
            signal_tensor = resampler(signal_tensor)
            
        # Add batch dimension
        signal_tensor = signal_tensor.unsqueeze(0)
        
        embedding = self.model.encode_batch(signal_tensor)
        
        # Ensure config dir exists
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(embedding, self.profile_path)
        self.enrolled_embedding = embedding
        logger.info("[VoiceBiometrics] Voice enrollment successful.")
        return True

    def verify_audio_chunk(self, pcm_data: bytes, sample_rate: int = 16000, threshold: float = 0.25) -> bool:
        """
        Verifies a raw PCM int16 audio chunk against the enrolled profile.
        Returns True if matched, False if not matched or no profile exists.
        """
        if self.enrolled_embedding is None:
            # If no profile is set up, default to allowing access
            return True
            
        if not pcm_data:
            return False
            
        self._load_model()
        
        try:
            # Convert raw PCM int16 to numpy float array
            audio_array = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Fast volume check (skip empty chunks)
            if np.mean(np.abs(audio_array)) < 0.005:
                return False
                
            signal_tensor = torch.tensor(audio_array).unsqueeze(0)
            
            if sample_rate != 16000:
                import torchaudio.transforms as T
                resampler = T.Resample(sample_rate, 16000)
                signal_tensor = resampler(signal_tensor)
                
            # Move to model device
            signal_tensor = signal_tensor.to(self.model.device)
            self.enrolled_embedding = self.enrolled_embedding.to(self.model.device)
            
            # Extract embedding for the chunk
            chunk_embedding = self.model.encode_batch(signal_tensor)
            
            # Calculate Cosine Similarity
            similarity = torch.nn.functional.cosine_similarity(chunk_embedding, self.enrolled_embedding, dim=-1)
            score = similarity.item()
            
            # Typically threshold for ECAPA is around 0.25 for VoxCeleb
            is_match = score > threshold
            return is_match
            
        except Exception as e:
            logger.error(f"[VoiceBiometrics] Verification error: {e}")
            return False

# Global singleton
voice_biometrics = VoiceBiometrics()
