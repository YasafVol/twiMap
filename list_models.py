import google.generativeai as genai
import os
from dotenv import load_dotenv

# Explicitly load from current directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

api_key = os.environ.get("GEMINI_API_KEY")
print(f"API Key present: {bool(api_key)}")

if api_key:
    genai.configure(api_key=api_key)
    try:
        print("Listing models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("No API Key found.")
