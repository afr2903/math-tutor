# Math voice tutor

## Requirements

- portaudio (Ubuntu `sudo apt-get install portaudio19-dev`)
- pyaudio
- python-dotenv
- openai
- pygame

**Note:** Check `requirements.txt`

It was developed using a python virtual environment

## Scripts

There are two Python files:

- `stream-speech.py`
- `tutor.py`

The first file highlights a tested function to stream the audio file as it is being generated. The difference is noted for larger files.

The second file receives audio, proccess it with `whisper` speech-to-text, then generates a response with the `gpt-4` model, and begins reproducing this response with a text-to-speech `tts-1` model.