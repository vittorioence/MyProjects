import os
from openai import OpenAI
from dotenv import load_dotenv
import traceback # Import traceback for detailed error info

# --- Your setup code ---
# IMPORTANT: Replace "sk-xxxx" with your actual key for testing,
# but NEVER commit your real key to version control!
# Use environment variables or a .env file in real projects.
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] =os.getenv("OPENAI_BASE_URL")
# --- End of your setup code ---

try:
    # Initialize the client *after* setting the environment variables.
    # Do NOT pass api_key or base_url here if relying on os.environ.
    client = OpenAI()

    print("Attempting to connect to:", os.environ["OPENAI_BASE_URL"])
    print("Using API Key starting with:", os.environ["OPENAI_API_KEY"][:6])

    # --- Example API Call ---
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", # Or whatever model your proxy service supports
        messages=[
            {"role": "system", "content": "You are a helpful assistant using a proxy."},
            {"role": "user", "content": "Ping!"}
        ],
        max_tokens=50
    )
    # --- End Example API Call ---

    print("\nConnection Successful!")
    print("Response:", response.choices[0].message.content)

except Exception as e:
    print(f"\nError connecting to the API:")
    print(f"Exception type: {type(e).__name__}")
    print(f"Error details: {e}")
    # Print detailed traceback for debugging network or config issues
    # print("\nTraceback:")
    # traceback.print_exc()