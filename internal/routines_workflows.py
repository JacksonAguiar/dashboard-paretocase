import json

from agno.agent import RunOutput

from database import register_usage


def _batch_send(phase: str, description: str, prompt_builder, filter_status: str = "confirmed"):
    from database import list_leads_by_status
    from agents import writer_agent

    for lead in list_leads_by_status(filter_status):
        channel = lead.get("channel") or "email"
        response: RunOutput = writer_agent.run_agent(
            input_data=prompt_builder(lead),
            channel=channel,
            lead_id=lead["id"],
            _event=phase,
        )
        register_usage(response, agent_name="Vigil Communication Writer Agent", phase=phase, description=description, lead_id=lead["id"])


def routine_confirmation():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a confirmation message for the Vigil Summit to:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Canal de envio: {channel}.\n"
            f"Confirm their spot, share agenda highlights and logistics."
        )
    _batch_send("routine_confirmation", "confirmation email", build)


def routine_followup():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a follow-up reminder for the Vigil Summit (1 day away) to:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Canal de envio: {channel}.\n"
            f"Reinforce the value of attending and create anticipation for tomorrow."
        )
    _batch_send("routine_followup", "1 day before: follow-up", build)


def routine_late_followup():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a last-minute follow-up for the Vigil Summit (2 hours away) to a late check-in:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Canal de envio: {channel}.\n"
            f"Short and direct: welcome them, share access info and any last-minute logistics."
        )
    _batch_send("routine_late_followup", "2h before: late check-in follow-up", build, filter_status="late_confirmed")


def routine_no_confirmation():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a no-confirmation alert for the Vigil Summit (1 day before the event) to a lead who has not yet confirmed:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Canal de envio: {channel}.\n"
            f"Urgently invite them to confirm their spot. Emphasize limited seats and value of attending."
        )
    _batch_send("routine_no_confirmation", "no-confirmation: 1 day before", build, filter_status="enriched")


def routine_engagement():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send an engagement message for the Vigil Summit (3 days before the event) to:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Canal de envio: {channel}.\n"
            f"Build anticipation, highlight key sessions relevant to their role and drive them toward confirming attendance."
        )
    _batch_send("routine_engagement", "engagement: 3 days before", build, filter_status="confirmed")


def routine_post_event_followup():
    from database import list_leads_by_status
    from agents.followup_agent import run_followup_agent

    for lead in list_leads_by_status("confirmed"):
        channel = lead.get("channel") or "email"
        data = lead.get("enriched_data") or {}
        input_data = {
            "lead_id": lead["id"],
            "name": lead["name"],
            "title": data.get("actual_title", lead["title"]),
            "company": lead["company"],
            "sector": data.get("sector", "N/A"),
            "technologies_used": data.get("technologies_used", []),
            "icp_score": data.get("icp_score", 0),
            "additional_data": lead.get("additional_data"),
        }
        run_followup_agent(
            input_data=json.dumps(input_data, ensure_ascii=False),
            lead_id=lead["id"],
            channel=channel,
        )


def routine_engagement_confirmed():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a final engagement message for the Vigil Summit (2 hours before the event) to a lead who confirmed via the no-confirmation message:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Canal de envio: {channel}.\n"
            f"Short and high-energy: share access link, agenda highlights and remind them of the value waiting for them today."
        )
    _batch_send("routine_engagement_confirmed", "engagement-confirmed: 2h before", build, filter_status="no_confirmation_confirmed")
