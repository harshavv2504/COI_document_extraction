import openai

import os

# Load the API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("❌ OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

def extract_json_from_md(system_prompt: str, user_input: str) -> str:
    """Send markdown + questions to OpenAI and return JSON string output."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )
    return response['choices'][0]['message']['content']
