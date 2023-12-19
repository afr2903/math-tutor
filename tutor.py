import os
from openai import OpenAI
from dotenv import load_dotenv
import threading
import pygame
import time

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

audio_file = open("input-audio/1.wav", "rb")
transcript = client.audio.translations.create(
    model="whisper-1",
    file=audio_file,
    #language="es",
    response_format="text"
)

print(transcript)

prompt = [
    {
        "role": "system",
        "content": "You are a virtual math tutor for a web platform focused on middle school students. You will receive a question asked by an student about a math problem and you will provide an easy to understand reasoning towards the solution. Avoid giving the answer directly, instead, try to guide the student towards the solution."
    },
    {
        "role": "user",
        "content": transcript
    }
]

stream = client.chat.completions.create(
    model="gpt-4",
    messages=prompt,
    stream=True,
)
complete_response = ""
tmp_response = ""
tts_ready = True
speech_ready = True
thread_id = 0

pygame.mixer.init()

def speak(input_text, id):
    global tts_ready
    global speech_ready

    print(f"Thread {id} started")
    print(input_text)

    sp_response = client.audio.speech.create(
        model="tts-1", 
        voice="onyx",
        input=input_text
    )

    
    tmp_path = f"output-{id}.opus"
    sp_response.stream_to_file(tmp_path)

    while not speech_ready:
        pass
    
    tts_ready = True
    speech_ready = False
    # Load and play the audio file
    pygame.mixer.music.load(tmp_path)
    
    #print(f"Time to play: {time.time() - start_time} seconds")
    pygame.mixer.music.play()

    # Loop to keep the script running during playback
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    speech_ready = True

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        #print(chunk.choices[0].delta.content, end="|", flush=True)
        tmp_response += chunk.choices[0].delta.content
        complete_response += chunk.choices[0].delta.content
        # if response has a space, send the string to another function
        # that will send the string to the API

        if " " in tmp_response and tts_ready:
            tts_input = ""
            space_count = 0
            space_idx = 0
            for i in reversed(range(len(tmp_response))):
                if tmp_response[i] == " ":
                    space_count += 1
                    if space_count == 1:
                        space_idx = i
            
            if space_count < 2:
                continue

            tts_input = tmp_response[:space_idx]
            tmp_response = tmp_response[space_idx:]
            tts_ready = False
            tmp_th = threading.Thread(target=speak, args=(tts_input,thread_id))
            tmp_th.start()
            thread_id += 1
            

print()

while not tts_ready:
    pass

print(complete_response)
speak(tmp_response, thread_id)

