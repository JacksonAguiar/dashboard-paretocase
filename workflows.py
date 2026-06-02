import json

from agno.agent import RunOutput

from database import save_lead, get_lead, update_status, update_channel, update_enriched_data, update_additional_data, register_usage
from agents import workflow_agent, normalization_agent


def normalize_lead(lead_data: dict) -> dict:
    response = normalization_agent.run(json.dumps(lead_data, ensure_ascii=False))
    register_usage(
        response,
        agent_name="Lead Normalization Agent",
        phase="phase_1_capture",
        description="Raw lead data normalization",
    )
    return response.content.model_dump()


def phase_1_capture(lead_data: dict) -> int:
    normalized = normalize_lead(lead_data)

    lead_id = save_lead(
        name=normalized["name"],
        email=normalized["email"],
        company=normalized["company"],
        title=normalized["title"],
        additional_data=normalized["additional_data"],
    )

    print(f"\n{'='*60}")
    print(f"[PHASE 1 - CAPTURE] Lead '{normalized['name']}' saved with ID {lead_id}")
    print(f"  Normalized data: {normalized['title']} @ {normalized['company']}")
    if normalized["additional_data"]:
        print(f"  Additional data: {list(normalized['additional_data'].keys())}")
    print("  Status: captured")
    print(f"{'='*60}")
    return lead_id


def phase_2_enrichment(lead_id: int) -> dict:
    lead = get_lead(lead_id)
    if lead is None:
        raise ValueError(f"Lead {lead_id} not found")

    print(f"\n{'='*60}")
    print(f"[PHASE 2 - ENRICHMENT] Enriching data for '{lead['name']}'...")
    print(f"{'='*60}")

    prompt = (
        f"Use the search_professional_data tool to find professional data for the lead:\n"
        f"- Email: {lead['email']}\n"
        f"- Company: {lead['company']}\n\n"
        f"After obtaining the data, return a summary of the information found."
    )

    response: RunOutput = workflow_agent.run(prompt)
    register_usage(
        response,
        agent_name="Vigil SDR Agent",
        phase="phase_2_enrichment",
        description="Search and summarize professional lead data",
        lead_id=lead_id,
    )
    print(f"\n[Agent]: {response.content}")

    from tools import search_professional_data
    raw_data = search_professional_data(lead["email"], lead["company"])
    data = json.loads(raw_data)

    update_enriched_data(lead_id, data)
    update_additional_data(lead_id, {"enrichment_source": "linkedin_mock", "enriched_at": json.dumps(data.get("icp_score", 0))})
    update_status(lead_id, "enriched")

    print("  Status updated: enriched")
    return data


def phase_3_engagement(lead_id: int):
    lead = get_lead(lead_id)
    if lead is None:
        raise ValueError(f"Lead {lead_id} not found")

    print(f"\n{'='*60}")
    print(f"[PHASE 3 - ENGAGEMENT] Engaging lead '{lead['name']}'...")
    print(f"{'='*60}")

    data = lead["enriched_data"]
    score = data.get("icp_score", 0)

    if score >= 80:
        priority = "HIGH"
        channel = "whatsapp"
    else:
        priority = "MEDIUM"
        channel = "email"

    print(f"  ICP Score: {score} | Priority: {priority} | Channel: {channel}")

    prompt = (
        f"Draft and send a confirmation message for the Vigil Summit.\n\n"
        f"Lead data:\n"
        f"- Name: {lead['name']}\n"
        f"- Title: {data.get('actual_title', lead['title'])}\n"
        f"- Company: {lead['company']}\n"
        f"- Sector: {data.get('sector', 'N/A')}\n"
        f"- Technologies used: {data.get('technologies_used', [])}\n"
        f"- ICP Score: {score}\n\n"
        f"Use the send_message tool with lead_id={lead_id} and channel='{channel}'.\n"
        f"The message should be personalized for the lead's context, mentioning how the event "
        f"is relevant to their role and the technologies they use."
    )

    response: RunOutput = workflow_agent.run(prompt)
    register_usage(
        response,
        agent_name="Vigil SDR Agent",
        phase="phase_3_engagement",
        description="Draft and send personalized confirmation message",
        lead_id=lead_id,
    )
    print(f"\n[Agent]: {response.content}")

    update_channel(lead_id, channel)
    update_status(lead_id, "confirmed")
    print("  Status updated: confirmed")


def phase_4_followup(lead_id: int, event_context: str):
    lead = get_lead(lead_id)
    if lead is None:
        raise ValueError(f"Lead {lead_id} not found")

    print(f"\n{'='*60}")
    print(f"[PHASE 4 - FOLLOW-UP] Post-event follow-up for '{lead['name']}'...")
    print(f"{'='*60}")

    data = lead["enriched_data"]

    prompt = (
        f"The Vigil Summit just ended. Do the post-event follow-up with this lead.\n\n"
        f"Lead data:\n"
        f"- Name: {lead['name']}\n"
        f"- Title: {data.get('actual_title', lead['title'])}\n"
        f"- Company: {lead['company']}\n"
        f"- Sector: {data.get('sector', 'N/A')}\n\n"
        f"Event context (what the lead watched/showed interest in):\n"
        f"{event_context}\n\n"
        f"Steps:\n"
        f"1. Use send_message (lead_id={lead_id}, channel='email') to send a personalized "
        f"follow-up message, thanking them for attending and connecting what was seen at the "
        f"event with a commercial meeting proposal.\n"
        f"2. Use schedule_meeting (lead_id={lead_id}) to schedule a Vigil.AI platform demo "
        f"meeting for next week."
    )

    response: RunOutput = workflow_agent.run(prompt)
    register_usage(
        response,
        agent_name="Vigil SDR Agent",
        phase="phase_4_followup",
        description="Post-event follow-up and meeting scheduling",
        lead_id=lead_id,
    )
    print(f"\n[Agent]: {response.content}")

    update_status(lead_id, "meeting_scheduled")
    print("  Status updated: meeting_scheduled")


def _batch_send(phase: str, description: str, prompt_builder, filter_status: str = "confirmed"):
    from database import list_leads_by_status
    for lead in list_leads_by_status(filter_status):
        response: RunOutput = workflow_agent.run(prompt_builder(lead))
        register_usage(response, agent_name="Vigil SDR Agent", phase=phase, description=description, lead_id=lead["id"])


def routine_confirmation():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a confirmation message for the Vigil Summit to:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Use send_message(lead_id={lead['id']}, channel='{channel}').\n"
            f"Confirm their spot, share agenda highlights and logistics."
        )
    _batch_send("routine_confirmation", "confirmation email", build)


def routine_followup():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a follow-up reminder for the Vigil Summit (1 day away) to:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Use send_message(lead_id={lead['id']}, channel='{channel}').\n"
            f"Reinforce the value of attending and create anticipation for tomorrow."
        )
    _batch_send("routine_followup", "1 day before: follow-up", build)


def routine_late_followup():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a last-minute follow-up for the Vigil Summit (2 hours away) to a late check-in:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Use send_message(lead_id={lead['id']}, channel='{channel}').\n"
            f"Short and direct: welcome them, share access info and any last-minute logistics."
        )
    _batch_send("routine_late_followup", "2h before: late check-in follow-up", build, filter_status="late_confirmed")


def routine_no_confirmation():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send a no-confirmation alert for the Vigil Summit (1 day before the event) to a lead who has not yet confirmed:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Use send_message(lead_id={lead['id']}, channel='{channel}').\n"
            f"Urgently invite them to confirm their spot. Emphasize limited seats and value of attending."
        )
    _batch_send("routine_no_confirmation", "no-confirmation: 1 day before", build, filter_status="enriched")


def routine_engagement():
    def build(lead):
        channel = lead.get("channel") or "email"
        return (
            f"Send an engagement message for the Vigil Summit (3 days before the event) to:\n"
            f"- Name: {lead['name']} | Title: {lead['title']} | Company: {lead['company']}\n\n"
            f"Use send_message(lead_id={lead['id']}, channel='{channel}').\n"
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
            f"Use send_message(lead_id={lead['id']}, channel='{channel}').\n"
            f"Short and high-energy: share access link, agenda highlights and remind them of the value waiting for them today."
        )
    _batch_send("routine_engagement_confirmed", "engagement-confirmed: 2h before", build, filter_status="no_confirmation_confirmed")
