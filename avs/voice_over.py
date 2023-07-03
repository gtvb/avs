import numpy as np
import wave
import struct

from srt_parser import parse_srt, to_milliseconds
from TTS.api import TTS

def generate_voice_over(transcription_path):
    # transcriptions = parse_srt(transcription_path)
    # wav_array = generate_wavs(transcriptions)

    # save_wav("output.wav", wav_array, 16000)
    model_name = TTS.list_models()[0]
    tts = TTS(model_name)
    # decreasing the length_scale fastens speech, great!
    # tts.synthesizer.tts_model.length_scale = 0.3
    tts.tts_to_file("This is a test! This is also a test! Testing velocity", speaker=tts.speakers[0], language=tts.languages[0])

def save_wav(filename, wav_array, sample_rate):
    with wave.open(filename, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)

        for sample in wav_array:
            sample = int(sample * (2 ** 15 - 1))
            f.writeframes(struct.pack("<h", sample))

# This function grabs a dictionary with the silences already
# inserted and generates all the wavs for those segments.
def generate_wavs(transcriptions):
    wav_array = []

    tts_model_config = prompt_tts_configs()
    model = tts_model_config["model"]

    print("Generating speech from chunks...")
    for chunk in transcriptions:
        if chunk["is_silence"]:
            silence_duration = to_milliseconds(chunk["end"]) - to_milliseconds(chunk["start"])
            wav_array.extend(generate_silence(silence_duration, 16000))
            continue

        print("Generating speech for chunk ", chunk["text"])
        wav = model.tts(chunk["text"], speaker=tts_model_config["speaker"], language=tts_model_config["language"])
        wav_array.extend(wav)
        
    return wav_array

def prompt_tts_configs():
    models = TTS.list_models()
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


def generate_silence(duration_ms, sampling_frequency):
    silent_wav = []
    total_samples = int((duration_ms / 1000) * sampling_frequency)
    for _ in range(0, total_samples):
        silent_wav.append(0)

    return silent_wav

if __name__ == "__main__":
    generate_voice_over("./resources/transcriptions/yeast.srt")    
