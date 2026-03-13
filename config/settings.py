
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///audit.db")
    GROK_API_KEY = os.getenv("GROK_API_KEY", "")

settings = Settings()
