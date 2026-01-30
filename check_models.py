import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
print("Checking available models with provided API key...")

try:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    # List models that support generateContent
    for m in client.models.list():
        if "generateContent" in m.supported_actions:
            print(f"Model: {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
