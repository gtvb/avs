## Estrutura do programa

```
usage: avs [-h] [--translate] [--with_transcription WITH_TRANSCRIPTION] [--save_srt SAVE_SRT] video_filename

Generate a transcribed video using the language of your choice!

positional arguments:
  video_filename

options:
  -h, --help            show this help message and exit
  --translate
  --with_transcription WITH_TRANSCRIPTION
  --save_srt SAVE_SRT
```

## Vídeo ./resources/videos/yeast.webm

Duração: 3m7s

- Com a flag `--with_transcriptions`:
real    4m38.972s
user    6m40.913s
sys     0m8.087s

- Com o processo de transcrição:
real    7m58.324s
user    16m46.873s
sys     0m22.620s

## Vídeo ./resources/videos/gpt-llama.mp4

Duração: 3m16s

- Com a flag `--with_transcriptions`:
real    6m49.077s (Descontar download do modelo)
user    10m43.698s
sys     0m12.011s

- Com o processo de transcrição:

real    9m21.437s
user    25m0.318s
sys     0m26.410s

real    11m43.461s
user    26m51.653s
sys     0m45.027s

