from openai import OpenAI

import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY")
)

def get_room_information(text, position):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {"role": "system", "content": "UGiven an OCR text output containing a concatenated room name and number with potential typos, process the text to extract and correct the room name and number. Check the extracted room name for spelling errors and correct them. Example input: lacturehall2024, Expected output: Lecture Hall 2024"},
            {"role": "user", "content": text,}
        ],
        max_tokens=300
    )

    return response.choices[0].message.content