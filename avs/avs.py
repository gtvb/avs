import argparse
import ffmpeg
import stable_whisper
import tempfile

from whisper.tokenizer import get_tokenizer
from voice_over import generate_voice_over
from translation import obtain_translated_transcription
from srt_utils import parse_srt

def main():
    parser = argparse.ArgumentParser(prog="avs", description="Generate a transcribed video using the language of your choice!")
    parser.add_argument("video_filename")
    parser.add_argument("--translate", action="store_true")
    parser.add_argument("--with_transcription")
    args = parser.parse_args()

    if not args.with_transcription: 
        print("Generating transcriptions for video...")
        tmp_transcription = tempfile.NamedTemporaryFile(suffix=".srt")
        generate_transcription(tmp_transcription.name, args.video_filename)

        transcriptions_path = tmp_transcription.name
    else:
        print("Transcriptions path already provided, skipping generation...")
        transcriptions_path = args.with_transcription

    if args.translate:
        tmp_transcriptions_handle = obtain_translated_transcription(transcriptions_path, "pt")
        transcriptions_path = tmp_transcriptions_handle.name
    else:
        print("Skipping translation process, moving on to speech generation...")

    transcriptions = parse_srt(transcriptions_path)

    tmp_generated_audio = tempfile.NamedTemporaryFile(suffix=".wav")
    generate_voice_over(transcriptions, tmp_generated_audio.name)

    # These are the three ffmpeg input sources that will be used on the merge and 
    # output operations. We merge the original audio with the generated one, and merge 
    # them. After that we need to select the original video's video stream, the merged 
    # audio and the transcriptions path, that can be translated or not (in the last case, 
    # the application would act like a dynamic reader).
    original_video_input = ffmpeg.input(args.video_filename)
    generated_audio_input = ffmpeg.input(tmp_generated_audio.name)
    transcription_input = ffmpeg.input(transcriptions_path)

    lowered_audio = original_video_input.audio.filter("volume", "0.1")

    merged_audio = ffmpeg.filter([lowered_audio, generated_audio_input], "amerge")
    output = ffmpeg.output(original_video_input.video, merged_audio, transcription_input, "avs.mp4", vcodec="copy", acodec="aac", **{"c:s": "mov_text"})

    ffmpeg.run(output)

    if args.translate:
        tmp_transcriptions_handle.close()
    tmp_generated_audio.close()

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
