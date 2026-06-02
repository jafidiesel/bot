import os
import logging
import subprocess
import speech_recognition as sr

def transcribe_voice(audio_file_path: str) -> str:
    wav_path = os.path.splitext(audio_file_path)[0] + '_conv.wav'
    try:
        subprocess.run(
            ['ffmpeg', '-i', audio_file_path, '-ac', '1', '-ar', '16000', '-y', wav_path],
            check=True, capture_output=True
        )

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language='es-AR')
        if not text:
            raise ValueError("No se detectó voz en el audio")
        return text

    except subprocess.CalledProcessError as e:
        raise ValueError(f"Error convirtiendo audio: {e.stderr.decode()}")
    except sr.UnknownValueError:
        raise ValueError("No se detectó voz en el audio")
    except sr.RequestError as e:
        raise ValueError(f"Error en el servicio de reconocimiento: {e}")
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
