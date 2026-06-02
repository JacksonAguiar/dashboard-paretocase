import os
import time
import uuid

_FROM_NUMBER = os.getenv("WHATSAPP_FROM_NUMBER", "+5511000000000")
_PROVIDER = os.getenv("WHATSAPP_PROVIDER", "mock")


def send_whatsapp(to_number: str, to_name: str, message: str) -> dict:
    time.sleep(0.2)

    message_id = f"wamid.mock-{uuid.uuid4().hex[:16]}"
    preview = message.replace("\n", " ")[:80]
    print(f"[WhatsApp:{_PROVIDER}] -> {to_name} ({to_number}): {preview}")

    return {
        "status": "sent",
        "channel": "whatsapp",
        "provider": _PROVIDER,
        "message_id": message_id,
        "from": _FROM_NUMBER,
        "to": to_number,
        "to_name": to_name,
        "body": message,
    }


def send_bulk(recipients: list[dict], message: str) -> list[dict]:
    return [
        send_whatsapp(
            to_number=r["number"],
            to_name=r.get("name", r["number"]),
            message=message,
        )
        for r in recipients
    ]
