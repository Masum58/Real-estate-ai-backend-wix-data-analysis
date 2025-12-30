import os
from dotenv import load_dotenv

load_dotenv()

RAW_DATA_API_URL = os.getenv("RAW_DATA_API_URL")
CLEAN_DATA_POST_API_URL = os.getenv("CLEAN_DATA_POST_API_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
