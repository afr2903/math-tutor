import soundfile as sf
import pyaudio
import requests
import io
import os
import pygame
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

def stream_audio(input_text):
    start_time = time.time()
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }
    data = {
        "model": "tts-1",
        "voice": "alloy",
        "input": input_text,
        "response_format": "opus",
    }

    audio = pyaudio.PyAudio()

    with requests.post(url, headers=headers, json=data, stream=True) as r:
        if r.status_code == 200:
            buffer = io.BytesIO()
            for chunk in r.iter_content(chunk_size=4096):
                buffer.write(chunk)
            buffer.seek(0)

            with sf.SoundFile(buffer, 'r') as sound_file:
                format = pyaudio.paInt16
                channels = sound_file.channels
                rate = sound_file.samplerate
                stream = audio.open(format=format, channels=channels, rate=rate, output=True)
                chunk_size = 1024
                data = sound_file.read(chunk_size, dtype='int16')
                print(f"Time taken: {time.time() - start_time}")

                while len(data) > 0:
                    stream.write(data.tobytes())
                    data = sound_file.read(chunk_size, dtype='int16')

                stream.stop_stream()
                stream.close()
        else:
            print("Error")

    audio.terminate()

    start_time = time.time()

    pygame.mixer.init()

    client = OpenAI()

    response = client.audio.speech.create(
        model="tts-1", 
        voice="alloy",
        input=input_text,
    )

    response.stream_to_file("output.opus")

    # Load and play the audio file
    pygame.mixer.music.load('output.opus')
    print(f"Time to play: {time.time() - start_time} seconds")
    pygame.mixer.music.play()

    # Loop to keep the script running during playback
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

if __name__ == "__main__":
    while True:
        text = input("Text: ")
        stream_audio(text)