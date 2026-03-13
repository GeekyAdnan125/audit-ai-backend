
import requests
from config.settings import settings

class LLMClient:

    def ask(self, prompt):

        if settings.GROK_API_KEY == "":
            return "No API key configured."

        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROK_API_KEY}"
            },
            json={
                "model": "grok-1",
                "messages": [{"role":"user","content":prompt}]
            }
        )

        return response.json()
