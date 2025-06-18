from dotenv import load_dotenv
import os
from google import genai
from pathlib import Path

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GOOGLE_CLIENT = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.0-flash"

_ROOT_PATH = Path(__file__).parent.resolve()
