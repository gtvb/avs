import tempfile
import subprocess
import soundfile as sf

import numpy as np
from srt_utils import parse_srt, to_milliseconds
from TTS.api import TTS

def generate_voice_over(transcriptions, out_path):
    wav_array = generate_wavs(transcriptions)
    sf.write(out_path, wav_array, 16000)

def generate_wavs(transcriptions):
    wav_array = []

    tts_model_config = prompt_tts_configs()
    model = tts_model_config["model"]

    tmp_generated_chunk = tmp_adjusted_chunk = None
    for chunk in transcriptions:
        optimal_duration = to_milliseconds(chunk["end"]) - to_milliseconds(chunk["start"])

        if chunk["is_silence"]:
            print(f"SILENCE, Generating and extending wav array...")
            silence = generate_silence(optimal_duration / 1000, 16000)
            wav_array.extend(silence)
            continue

        tmp_generated_chunk = tempfile.NamedTemporaryFile()
        model.tts_to_file(chunk["text"], speaker=tts_model_config["speaker"], language=tts_model_config["language"], file_path=tmp_generated_chunk.name)

        out_info = sf.info(tmp_generated_chunk.name)
        generated_wav_duration = (out_info.frames / out_info.samplerate) * 1000

        tmp_adjusted_chunk = tempfile.NamedTemporaryFile()
        subprocess.run(["rubberband", "-3", tmp_generated_chunk.name, tmp_adjusted_chunk.name, "--time", str(optimal_duration / generated_wav_duration)])

        data, _ = sf.read(tmp_adjusted_chunk.name)

        wav_array.extend(data)

    if tmp_adjusted_chunk is not None and tmp_generated_chunk is not None:
        tmp_generated_chunk.close()
        tmp_adjusted_chunk.close()

    return wav_array

def prompt_tts_configs():
    tts_instance = TTS()
    models = tts_instance.list_models()
    for i in range(0, len(models)):
        print(f"{i+1}) {models[i]}")

    selected_model_index = int(input("Select a model: "))
    model = TTS(models[selected_model_index - 1], progress_bar=True)

    language = None
    if model.is_multi_lingual:
        languages = model.languages
        for i in range(0, len(languages)):
            print(f"{i+1}) {languages[i]}")

        selected_language_index = int(input("Select a language: "))
        language = languages[selected_language_index - 1]

    speaker = None
    if model.is_multi_speaker:
        speakers = model.speakers
        for i in range(0, len(speakers)):
            print(f"{i+1}) {speakers[i]}")

        selected_speaker_index = int(input("Select a speaker: "))
        speaker = speakers[selected_speaker_index - 1]

    return {
            "model": model,
            "speaker": speaker,
            "language": language
    }

def generate_silence(duration, samplerate):
    silent_wav = []
    total_samples = int(duration * samplerate)
    for _ in range(0, total_samples):
        silent_wav.append(0)

    return silent_wav
