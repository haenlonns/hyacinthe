from openai import OpenAI

import os
import base64
from dotenv import load_dotenv

from constants import *

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY")
)

def get_room_number(command):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You will receive a room number to navigate to. Convert the following spoken number to a numerical representation. If not a number, return -1."},
            {"role": "user", "content": f"Convert the following spoken room number to a numerical representation: '{command}'. If not a number, return -1."}
        ],
        max_tokens=100
    )
    print("Check")
    return int(response.choices[0].message.content)

def find_closest_command(command, commands):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {"role": "system", "content": "The user is asking for a command that is similar to the one they provided. Out of the provided list, pick command a command from the list that is most similar to the one they provided. If none match, pick the final item in the list. Respond only with one command spelled exactly like the command list."},
            {"role": "user", "content": "List of commands: " + ", ".join(commands) + "." + f"User command: {command}"}
        ],
        max_tokens=300
    )

    print(response.choices[0].message.content)
    if(response.choices[0].message.content == "NAVIGATE"):
        return response.choices[0].message.content, get_room_number(command)

    return response.choices[0].message.content, None

if __name__ == "__main__":
    print(find_closest_command("bleh bleh bleh", ["where am I", "help me find room", "try again"]))