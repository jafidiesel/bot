import os
import logging
import resource
import subprocess
import time
import speech_recognition as sr

def transcribe_voice(audio_file_path: str) -> tuple[str, dict]:
    wav_path = os.path.splitext(audio_file_path)[0] + '_conv.wav'
    ru_before = resource.getrusage(resource.RUSAGE_SELF)
    t_total = time.perf_counter()
    try:
        t0 = time.perf_counter()
        subprocess.run(
            ['ffmpeg', '-i', audio_file_path, '-ac', '1', '-ar', '16000', '-y', wav_path],
            check=True, capture_output=True
        )
        t_ffmpeg = time.perf_counter() - t0

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        t0 = time.perf_counter()
        text = recognizer.recognize_google(audio_data, language='es-AR')
        t_api = time.perf_counter() - t0

        if not text:
            raise ValueError("No se detectó voz en el audio")

        ru_after = resource.getrusage(resource.RUSAGE_SELF)
        stats = {
            'ffmpeg_s': round(t_ffmpeg, 2),
            'api_s': round(t_api, 2),
            'total_s': round(time.perf_counter() - t_total, 2),
            'cpu_s': round((ru_after.ru_utime + ru_after.ru_stime) - (ru_before.ru_utime + ru_before.ru_stime), 2),
            'mem_mb': round(ru_after.ru_maxrss / 1024, 1),
        }
        logging.info(
            f"[transcribe] ffmpeg={stats['ffmpeg_s']}s | api={stats['api_s']}s | "
            f"total={stats['total_s']}s | cpu={stats['cpu_s']}s | mem={stats['mem_mb']}MB"
        )
        return text, stats

    except subprocess.CalledProcessError as e:
        raise ValueError(f"Error convirtiendo audio: {e.stderr.decode()}")
    except sr.UnknownValueError:
        raise ValueError("No se detectó voz en el audio")
    except sr.RequestError as e:
        raise ValueError(f"Error en el servicio de reconocimiento: {e}")
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
