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

    return response

def find_closest_command(command, commands):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {"role": "system", "content": "The user is asking for a command that is similar to the one they provided. Out of the provided list, pick command a command from the list that is most similar to the one they provided. If none match, pick the final item in the list. Respond only with one command spelled exactly like the command list."},
            {"role": "user", "content": "List of commands: " + ", ".join(commands) + "." + f"User command: {command}"}
        ],
        max_tokens=300
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print(find_closest_command("bleh bleh bleh", ["where am I", "help me find room", "try again"]))