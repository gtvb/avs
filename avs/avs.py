import argparse
import ffmpeg
import stable_whisper
import tempfile

from whisper.tokenizer import get_tokenizer
from voice_over import generate_voice_over

def main():
    parser = argparse.ArgumentParser(prog="avs", description="Generate a transcribed video using the language of your choice!")
    parser.add_argument("video_filename")
    args = parser.parse_args()

    tmp_transcription = tempfile.NamedTemporaryFile(suffix=".srt")
    generate_transcription(tmp_transcription.name, args.video_filename)

    tmp_generated_audio = tempfile.NamedTemporaryFile(suffix=".wav")
    generate_voice_over(tmp_transcription.name, tmp_generated_audio.name)

    original_video_input = ffmpeg.input(args.video_filename)
    generated_audio_input = ffmpeg.input(tmp_generated_audio.name)
    transcription_input = ffmpeg.input(tmp_transcription.name)

    lowered_audio = original_video_input.audio.filter("volume", "0.1")

    merged_audio = ffmpeg.filter([lowered_audio, generated_audio_input], "amerge")
    output = ffmpeg.output(original_video_input.video, merged_audio, transcription_input, "avs.mp4", vcodec="copy", acodec="aac", **{"c:s": "mov_text"})

    ffmpeg.run(output)


def generate_transcription(transcription_out, audio_stream):
    tokenizer = get_tokenizer(multilingual=True)
    number_tokens = [
        i for i in range(tokenizer.eot) if all(c in "0123456789" for c in tokenizer.decode([i]).removeprefix(" "))
    ]
    model = stable_whisper.load_model("base")

    result = model.transcribe(audio_stream, regroup=False, suppress_tokens=[-1] + number_tokens)
    (
        result
        .split_by_punctuation([('.', ' '), '。', '?', '？', ',', '，'])
        .split_by_gap(.5)
        .merge_by_gap(.35, max_words=8)
        .split_by_punctuation([('.', ' '), '。', '?', '？'])
    )

    result.to_srt_vtt(transcription_out, word_level=False)

if __name__ == "__main__":
    main() 
