import numpy as np
from avs.srt_parser import parse_srt, to_milliseconds
import wave

def generate_voice_over(transcription_path):
    transcriptions = parse_srt(transcription_path)
    wavs = generate_wavs(transcriptions)

# This function grabs a dictionary with the silences already
# inserted and generates all the wavs for those segments.
def generate_wavs(transcriptions):
    wavs = []

    tts_model_config = prompt_tts_configs()
    model = TTS(tts_model_config["model_name"])

    for chunk in transcriptions:
        if chunk["is_silence"]:
            silence_duration = to_milliseconds(chunk["end"]) - to_milliseconds(chunk["start"])
            wavs.append(generate_silence(silence_duration))
            continue

        # Returns a dictionary containing data about the model to be run
        # assumes the format:
        # "model_name": str,
        # "is_multilingual": bool,
        # "model_speaker": str | nil,
        # "model_language": str | nil,
        if tts_model_config["is_multilingual"]:
            wav = model.tts(chunk["text"], speaker=tts_model_config["model_speaker"], language=tts_model_config["model_language"])
            wavs.append(wav)

        return wavs

def prompt_tts_configs():
    models = TTS.list_models()
    for i in range(0, len(models)):
        print(f"{i+1}) {models[i]}")

    selected_model_index = int(input("Select a model: "))
    selected_model = models[selected_model_index]

    return {}


def generate_silence(duration_ms):
    # For "CD quality" sampling frequency, you need 44100Hz
    # (that is the standard sampling frequency for consumer audio).
    sampling_frequency = 44100

    total_samples = int((duration_ms / 1000) * sampling_frequency)
    silence_audio = np.zeros(total_samples, dtype=np.float32)

    # Create a WAV file in memory
    wav_file = wave.open('silence.wav', 'wb')
    wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit audio)
    wav_file.setframerate(sampling_frequency)
    wav_file.setnchannels(1)  # Mono audio

    # Write the silence audio data to the WAV file
    wav_file.writeframes(silence_audio.tobytes())

    # Close the WAV file
    wav_file.close()

    # Read the contents of the WAV file
    with open('silence.wav', 'rb') as file:
        wav_data = file.read()

    return wav_data

if __name__ == "__main__":
    generate_voice_over("./yeast.srt")    
