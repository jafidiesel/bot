import os
import json
import logging
from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'vosk-model-es')

def _convert_to_wav(audio_file_path: str) -> str:
    """Convert audio file to mono 16kHz 16-bit WAV. Returns path to WAV file."""
    wav_path = os.path.splitext(audio_file_path)[0] + '_converted.wav'
    audio = AudioSegment.from_file(audio_file_path)
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    audio.export(wav_path, format='wav')
    return wav_path

def transcribe_voice(audio_file_path: str) -> str:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Vosk Spanish model not found at {MODEL_PATH}\n"
            "Please download the model from https://alphacephei.com/vosk/models"
        )

    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

    wav_path = None
    try:
        wav_path = _convert_to_wav(audio_file_path)

        model = Model(MODEL_PATH)
        recognizer = KaldiRecognizer(model, 16000)

        transcribed_text = ""
        with wave.open(wav_path, "rb") as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result.get('text'):
                        transcribed_text += result['text'] + " "

            final_result = json.loads(recognizer.FinalResult())
            if final_result.get('text'):
                transcribed_text += final_result['text']

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
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
