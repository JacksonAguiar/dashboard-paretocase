from database import save_funil_approch, list_funil_approchs


def create_funil_approch(user_id: int, approuch: str, mensagem: str, channel: str | None = None) -> dict:
    approch_id = save_funil_approch(user_id, approuch, mensagem, channel)
    return {
        "id": approch_id,
        "user_id": user_id,
        "approuch": approuch,
        "mensagem": mensagem,
        "channel": channel,
    }


def get_funil_approchs(user_id: int) -> list[dict]:
    return list_funil_approchs(user_id)
