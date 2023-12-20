import os
from openai import OpenAI
from dotenv import load_dotenv
import threading
import pygame
import pyaudio
import math
import struct
import wave
import time

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
tts_ready = True
speech_ready = True

Threshold = 10

SHORT_NORMALIZE = (1.0/32768.0)
chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
swidth = 2

TIMEOUT_LENGTH = 3

f_name_directory = "input-audio"

class Recorder:

    @staticmethod
    def rms(frame):
        count = len(frame) / swidth
        format = "%dh" % (count)
        shorts = struct.unpack(format, frame)

        sum_squares = 0.0
        for sample in shorts:
            n = sample * SHORT_NORMALIZE
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)

        return rms * 1000

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=chunk)

    def record(self):
        print('Noise detected, recording beginning')
        rec = []
        current = time.time()
        end = time.time() + TIMEOUT_LENGTH

        while current <= end:

            data = self.stream.read(chunk)
            if self.rms(data) >= Threshold: end = time.time() + TIMEOUT_LENGTH

            current = time.time()
            rec.append(data)
        self.write(b''.join(rec))

    def write(self, recording):
        n_files = len(os.listdir(f_name_directory))

        filename = os.path.join(f_name_directory, '{}.wav'.format(n_files))

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(recording)
        wf.close()
        print('Written to file: {}'.format(filename))
        
        audio_file = open(filename, "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="es",
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

        global tts_ready
        global speech_ready
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
                    
                    if space_count < 3:
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
        print('Returning to listening')



    def listen(self):
        print('Listening beginning')
        while True:
            input = self.stream.read(chunk)
            rms_val = self.rms(input)
            if rms_val > Threshold:
                self.record()

a = Recorder()

a.listen()



