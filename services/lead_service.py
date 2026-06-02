from database import (
    save_lead,
    get_lead,
    get_lead_by_email,
    get_lead_by_user_code,
    update_lead,
    update_status,
    update_channel,
    update_enriched_data,
    update_additional_data,
    update_planner_result,
    update_followup_instructions,
    add_interaction,
    list_leads_by_status,
)


def create_lead(name: str, email: str, company: str, title: str, additional_data: dict | None = None, channel: str | None = None, user_code: str | None = None) -> dict:
    lead_id = save_lead(name, email, company, title, additional_data, channel, user_code)
    return get_lead(lead_id)


def get_lead_by_id(lead_id: int) -> dict | None:
    return get_lead(lead_id)


def get_lead_by_email_address(email: str) -> dict | None:
    return get_lead_by_email(email)


def get_lead_by_code(user_code: str) -> dict | None:
    return get_lead_by_user_code(user_code)


def update(lead_id: int, **kwargs) -> bool:
    return update_lead(lead_id, **kwargs)


def set_status(lead_id: int, status: str) -> None:
    update_status(lead_id, status)


def set_channel(lead_id: int, channel: str) -> None:
    update_channel(lead_id, channel)


def set_enriched_data(lead_id: int, data: dict) -> None:
    update_enriched_data(lead_id, data)


def merge_additional_data(lead_id: int, data: dict) -> None:
    update_additional_data(lead_id, data)


def set_planner_result(lead_id: int, result: str) -> None:
    update_planner_result(lead_id, result)


def set_followup_instructions(lead_id: int, instructions: str) -> None:
    update_followup_instructions(lead_id, instructions)


def record_interaction(lead_id: int, type_: str, content: str) -> None:
    add_interaction(lead_id, type_, content)


def list_by_status(status: str) -> list[dict]:
    return list_leads_by_status(status)
