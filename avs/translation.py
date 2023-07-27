import tempfile
from deep_translator import GoogleTranslator

def obtain_translated_transcription(original_file_path, language_code):
    translator = GoogleTranslator(source="auto", target=language_code)
    translated_transcriptions_tmp = tempfile.NamedTemporaryFile(suffix=".srt")

    with open(original_file_path, "r") as original_file:
        contents = original_file.read().split("\n")
        translated_list = []

        for i in range(2, len(contents), 4):
            before_text_list = contents[i-2:i]
            translated_text = translator.translate(contents[i]) + "\n"
            before_text_list.append(translated_text)
            translated_list.extend(before_text_list)

    tf = open(translated_transcriptions_tmp.name, "w")
    tf.write("\n".join(translated_list))

    return translated_transcriptions_tmp

