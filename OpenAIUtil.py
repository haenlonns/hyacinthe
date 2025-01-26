from openai import OpenAI

import os
import base64
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY")
)


def get_room_information(base64_image, position):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {"role": "system", "content": "You will receive an image of a room sign with a room name and number. Please only return what the room name and number are. If you're unsure, return an empty string."},
            {"role": "user", "content": {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            }}
        ],
        max_tokens=300
    )

    return response.choices[0].message.content