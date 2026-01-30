
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    print("No API Key")
    exit()

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5)
try:
    response = llm.invoke("Say hello")
    print(f"Content type: {type(response.content)}")
    print(f"Content: {response.content}")
except Exception as e:
    print(f"Error: {e}")
