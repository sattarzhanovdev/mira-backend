from .context import build_trip_system_prompt

MAX_HISTORY = 4  # максимум 4 последних сообщения


def build_messages_for_ai(trip):
    messages = [
        {
            "role": "system",
            "content": build_trip_system_prompt(trip),
        }
    ]

    qs = trip.messages.order_by("-created_at")[:MAX_HISTORY]
    history = reversed(qs)

    for msg in history:
        messages.append(
            {
                "role": msg.role,
                "content": msg.content[:1000],  # защита от длинного текста
            }
        )

    return messages
