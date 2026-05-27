import os
import json
import logging
from vosk import Model, KaldiRecognizer
import wave

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'vosk-model-es')

def transcribe_voice(audio_file_path: str) -> str:
    """
    Transcribe voice audio file using Vosk with Spanish model.
    
    Args:
        audio_file_path: Path to the audio file (WAV, OGG, etc.)
    
    Returns:
        Transcribed text in Spanish
        
    Raises:
        FileNotFoundError: If model or audio file not found
        ValueError: If audio format is not supported
        Exception: For other Vosk/audio processing errors
    """
    
    # Verify model exists
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Vosk Spanish model not found at {MODEL_PATH}\n"
            "Please download the model from https://alphacephei.com/vosk/models"
        )
    
    # Verify audio file exists
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    try:
        # Initialize Vosk model and recognizer
        model = Model(MODEL_PATH)
        recognizer = KaldiRecognizer(model, 16000)
        recognizer.SetWords(json.dumps({}))  # Empty word list for open vocabulary
        
        # Open and process audio file
        with wave.open(audio_file_path, "rb") as wf:
            # Verify audio format
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
                raise ValueError(
                    "Audio must be mono 16kHz PCM WAV\n"
                    f"Current format: {wf.getnchannels()} channels, "
                    f"{wf.getsampwidth()} bytes, {wf.getframerate()}Hz"
                )
            
            # Process audio in chunks
            transcribed_text = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if 'result' in result:
                        transcribed_text += " ".join([item['conf'] for item in result['result']])
            
            # Get final result
            final_result = json.loads(recognizer.FinalResult())
            if 'result' in final_result:
                transcribed_text += " ".join([item['conf'] for item in final_result['result']])
            
            if not transcribed_text.strip():
                raise ValueError("No speech detected in audio file")
            
            return transcribed_text.strip()
    
    except wave.Error as e:
        raise ValueError(f"Invalid audio file format: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error processing Vosk response: {str(e)}")
    except Exception as e:
        logging.error(f"Transcription error: {str(e)}", exc_info=True)
        raise
