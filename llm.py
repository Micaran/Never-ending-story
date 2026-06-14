import os
from dotenv import load_dotenv
from groq import Groq
import json

import re

def safe_json_loads(content):
    content = content.strip()
    
    # Quitar fences markdown si los hay
    if content.startswith("```"):
        content = re.sub(r"^```(json)?\s*|\s*```$", "", content.strip())
    
    content = content.strip()
    
    # Intento directo primero
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Si falla: escapar SOLO los saltos de línea que están DENTRO de strings JSON.
    # Recorremos carácter por carácter, trackeando si estamos dentro de un string.
    result = []
    in_string = False
    escape = False
    for ch in content:
        if escape:
            result.append(ch)
            escape = False
            continue
        if ch == '\\':
            result.append(ch)
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            result.append(ch)
            continue
        if in_string and ch == '\n':
            result.append('\\n')
            continue
        if in_string and ch == '\r':
            result.append('\\r')
            continue
        if in_string and ch == '\t':
            result.append('\\t')
            continue
        result.append(ch)
    
    fixed = "".join(result)
    return json.loads(fixed)


def load_client():
    load_dotenv()  # reads the .env file and loads variables into the environment
    
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        print("ERROR: GROQ_API_KEY not found in .env file.")
        print("Make sure your .env file exists and has the key.")
        exit(1)
    
    client = Groq(api_key=api_key)
    return client


def test_connection(client):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say hello in one sentence."}
            ]
        )
        print("Connection test passed!")
        print("LLM says:", response.choices[0].message.content)
        return True
    except Exception as e:
        print("Connection test FAILED:", str(e))
        return False
    
def build_character_prompt(era):
    prompt = f"""You are a creative storyteller. Generate a character for an interactive adventure game.

    Setting: {era["name"]} ({era["years"]})
    Context: {era["llm_context"]}

    Create a character with the following sections, using exactly these labels:
    - Name: (full name and nickname if appropriate)
    - Role: (their job or position in society, one line)
    - Background: (2-3 sentences about their history)
    - Personality: (2-3 short sentences about how they act)
    - Your destiny: (1-2 sentences hinting at the adventure ahead, spoken to the player as "you")

    Be creative and specific. Avoid generic names. Make the character feel real.
    Return ONLY valid JSON in this format:

    {{
    "name": "",
    "role": "",
    "background": "",
    "personality": "",
    "destiny": ""
    }}

    Do not include markdown.
    Do not include explanations.
    Return only JSON.
    """
    
    return prompt

def generate_character(client, era):
    prompt = build_character_prompt(era)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=600,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content

    return json.loads(content)


def display_character(character_text):
    print("-" * 50)
    print("YOUR CHARACTER")
    print("-" * 50)
    print(character_text["name"])
    print("-" * 50)
    print(character_text["role"])
    print("-" * 50)
    print(character_text["background"])
    print("-" * 50)
    print(character_text["personality"])
    print("-" * 50)
    print(character_text["destiny"])

def build_intro_prompt(era, character):
    prompt = f"""
        You are a master storyteller writing an interactive adventure.

        Setting: {era["name"]} ({era["years"]})
        Context: {era["llm_context"]}

        The player's character:
        Name: {character["name"]}
        Role: {character["role"]}
        Background: {character["background"]}
        Personality: {character["personality"]}
        Destiny: {character["destiny"]}

        Write the opening scene of the story.

        Requirements:
        - Write 3 to 5 atmospheric paragraphs.
        - Speak directly to the player using "you".
        - End with a dramatic decision moment.
        - Create exactly 3 meaningful choices.

        Return ONLY valid JSON in this format:

        {{
            "story": "the full opening scene",
            "choices": [
                "first option",
                "second option",
                "third option"
            ]
        }}

        Do not include markdown.
        Do not include explanations.
        Return only JSON.
        """
    return prompt

def generate_intro(client, era, character_text):
    prompt = build_intro_prompt(era, character_text)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    content = response.choices[0].message.content

    return json.loads(content)

def display_story_segment(segment, chapter_title):
    print("─" * 49)
    print(chapter_title)
    print("─" * 49)
    print()

    print(segment["story"])
    print()

    print("─" * 49)


def build_system_prompt(era, character_text):
    return f"""You are a master storyteller running an interactive adventure game.

    Setting: {era["name"]} ({era["years"]})
    World context: {era["llm_context"]}

    The player's character:
    {character_text}

    Rules you must always follow:
    - Write in second person ("you" not "they")
    - Each response must be 3-5 paragraphs of atmospheric storytelling
    - Keep choices meaningfully different from each other
    - Remember everything that has happened in the story so far
    - Build on previous choices — actions have consequences
    - Maintain the tone and atmosphere of the era throughout
    - Never break the fourth wall or acknowledge you are an AI

    Return ONLY valid JSON in this format:

        {{
            "story": "the full scene",
            "choices": [
                "first option",
                "second option",
                "third option"
            ]
        }}

        Do not include markdown.
        Do not include explanations.
        Return only JSON.
"""

def initialize_history(intro):
    history = [
        {
            "role": "assistant",
            "content": intro["story"]
        }
    ]
    return history

def add_to_history(history, role, content):
    history.append({"role": role, "content": content})

def generate_continuation(client, era, character_text, history, player_choice):
    add_to_history(history, "user", f"I choose: {player_choice}")
    
    system_message = {"role": "system", "content": build_system_prompt(era, character_text)}
    messages_with_system = [system_message] + history
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=messages_with_system,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    story_text = safe_json_loads(content)
    
    add_to_history(
        history,
        "assistant",
        story_text["story"]
    )
    
    return story_text


# from settings import ERAS
# client = load_client()
# character = generate_character(client, ERAS[0])
# display_character(character)
# #print(character)