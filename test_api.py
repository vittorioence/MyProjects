import os
from dotenv import load_dotenv

# --- Choose ONE of the sections below based on your provider ---

# --- OpenAI Section ---
from openai import OpenAI
load_dotenv() # Load variables from .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # Or other available model like gpt-4
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
    )
    print("OpenAI Connection Successful!")
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print(f"Error connecting to OpenAI: {e}")
# --- End OpenAI Section ---

# --- Anthropic Section ---
# import anthropic
# load_dotenv() # Load variables from .env file
# client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
# try:
#     message = client.messages.create(
#         model="claude-3-opus-20240229", # Or other available model like claude-3-sonnet...
#         max_tokens=100,
#         messages=[
#             {"role": "user", "content": "Hello!"}
#         ]
#     )
#     print("Anthropic Connection Successful!")
#     print("Response:", message.content[0].text)
# except Exception as e:
#     print(f"Error connecting to Anthropic: {e}")
# --- End Anthropic Section ---