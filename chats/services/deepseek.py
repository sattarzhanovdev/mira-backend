# chats/services/deepseek.py
import requests
from django.conf import settings
from requests.exceptions import Timeout, RequestException


class DeepSeekError(Exception):
    pass


def ask_deepseek(messages: list[dict]) -> str:
    try:
        response = requests.post(
            f"{settings.DEEPSEEK_BASE_URL}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": messages,
            },
            timeout=60,
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except Timeout:
        raise DeepSeekError("DeepSeek timeout")

    except RequestException as e:
        raise DeepSeekError(str(e))
