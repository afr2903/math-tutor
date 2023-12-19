import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

audio_file = open("input-audio/1.wav", "rb")
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
        "content": "You are a virtual math tutor for a web platform focused on middle school students.You will receive a question asked by an student about a math problem and you will provide an easy to understand reasoning towards the solution. Avoid giving the answer directly, instead, try to guide the student towards the solution."
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
response = ""

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="|", flush=True)
        response += chunk.choices[0].delta.content

print()

print(response)