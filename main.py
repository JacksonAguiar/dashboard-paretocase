import json

from dotenv import load_dotenv

load_dotenv()

from database import (
    init_db,
    save_lead,
    get_lead,
    update_enriched_data,
    update_status,
    update_channel,
    register_usage,
    list_usage,
    list_funil_approchs as get_funil_approchs,
)
from tools import search_professional_data
from agents.planner_agent import planner_agent
from agents import writer_agent

MOCK_LEADS = [
    {
        "name": "  Ricardo Mendes  ",
        "email": "  Ricardo.CTO@techshield.com.br ",
        "company": "TechShield  Solutions",
        "title": "chief technology officer",
        "phone": "+55 11 99999-0001",
        "source": "landing_page_vigil_summit",
        "utm_source": "linkedin_ads",
    },
    {
        "name": "Camila Ferreira",
        "email": "camila.ferreira@bancoseguro.com.br",
        "company": "Banco Seguro S.A.",
        "title": "information security analyst",
        "phone": "+55 21 98888-0002",
        "source": "partner_referral",
        "department": "SOC / Blue Team",
    },
]

EVENT_CONTEXTS = {
    "Ricardo Mendes": (
        "Attended the talk 'Generative AI for Real-Time Threat Detection'. "
        "Asked 3 questions about SIEM Splunk integration. "
        "Visited the Vigil.AI booth and requested a demo of the auto-triage feature."
    ),
    "Camila Ferreira": (
        "Watched the panel 'Zero Trust in Practice for Financial Institutions'. "
        "Showed interest in SOC automation. "
        "Exchanged business cards with the Vigil.AI Head of Product."
    ),
}


def _capture(lead_data: dict) -> int:
    base_keys = {"name", "email", "company", "title"}
    additional = {k: v for k, v in lead_data.items() if k not in base_keys}
    lead_id = save_lead(
        name=lead_data["name"].strip(),
        email=lead_data["email"].strip().lower(),
        company=lead_data["company"].strip(),
        title=lead_data["title"].strip(),
        additional_data=additional,
    )
    print(f"\n{'='*60}")
    print(f"[CAPTURE] Lead '{lead_data['name'].strip()}' saved with ID {lead_id}")
    print(f"{'='*60}")
    return lead_id


def _enrich(lead_id: int) -> dict:
    lead = get_lead(lead_id)
    data = json.loads(search_professional_data(lead["email"], lead["company"], lead["title"]))
    profile = data.get("profile", {})
    channel = profile.get("recommended_channel") or ("whatsapp" if profile.get("icp_score", 0) >= 80 else "email")

    update_enriched_data(lead_id, data)
    update_channel(lead_id, channel)
    update_status(lead_id, "enriched")

    print(f"[ENRICH] role={data.get('detected_role_key')} | icp={profile.get('icp_score')} | channel={channel}")
    return data


def _plan(lead_id: int):
    lead = get_lead(lead_id)
    prompt = (
        f"Elabore o plano de abordagem para o seguinte lead do Vigil Summit:\n\n"
        f"- Nome: {lead['name']}\n"
        f"- Email: {lead['email']}\n"
        f"- Cargo: {lead['title']}\n"
        f"- Empresa: {lead['company']}\n"
        f"- Enriquecimento: {json.dumps(lead.get('enriched_data') or {}, ensure_ascii=False)}\n"
    )
    response = planner_agent.run(prompt)
    register_usage(response, agent_name="Vigil Sales Strategist Agent", phase="phase_planner", description="Pre-event engagement plan", lead_id=lead_id)
    print(f"[PLAN] {str(response.content)[:120]}...")


def _engage(lead_id: int, data: dict, channel: str):
    profile = data.get("profile", {})
    brief = (
        f"Escreva a mensagem de engajamento pré-evento (confirmação de presença) para o lead.\n"
        f"- Cargo: {profile.get('actual_title')}\n"
        f"- Setor: {profile.get('sector')}\n"
        f"- Tecnologias: {profile.get('technologies_used')}\n"
        f"- ICP score: {profile.get('icp_score')}\n"
        f"Canal de envio: {channel}.\n"
        f"Personalize conectando o evento ao papel e às tecnologias do lead."
    )
    response = writer_agent.run_agent(input_data=brief, channel=channel, lead_id=lead_id, _event="engagement")
    register_usage(response, agent_name="Vigil Communication Writer Agent", phase="phase_engagement", description="Pre-event engagement message", lead_id=lead_id)
    update_status(lead_id, "confirmed")


def _followup(lead_id: int, channel: str, event_context: str):
    brief = (
        f"Escreva a mensagem de follow-up pós-evento para o lead.\n"
        f"Contexto do que o lead viu/demonstrou interesse no evento:\n{event_context}\n"
        f"Canal de envio: {channel}.\n"
        f"Agradeça a presença e proponha uma conversa/demonstração da plataforma Vigil.AI."
    )
    response = writer_agent.run_agent(input_data=brief, channel=channel, lead_id=lead_id, _event="post_event_followup")
    register_usage(response, agent_name="Vigil Communication Writer Agent", phase="phase_followup", description="Post-event follow-up message", lead_id=lead_id)
    update_status(lead_id, "meeting_scheduled")


def execute_full_flow(lead_data: dict, event_context: str):
    lead_id = _capture(lead_data)
    data = _enrich(lead_id)
    channel = get_lead(lead_id).get("channel") or "email"
    _plan(lead_id)
    _engage(lead_id, data, channel)
    _followup(lead_id, channel, event_context)

    final_lead = get_lead(lead_id)
    approaches = get_funil_approchs(lead_id)
    print(f"\n{'#'*60}")
    print(f"FINAL SUMMARY - {final_lead['name']}")
    print(f"{'#'*60}")
    print(f"  Status: {final_lead['funnel_status']}")
    print(f"  Enriched data: {json.dumps(final_lead['enriched_data'], indent=2, ensure_ascii=False)}")
    print(f"  Total approaches: {len(approaches)}")
    for i, approach in enumerate(approaches, 1):
        print(f"    {i}. [{approach['channel']}] {approach['approuch']}: {str(approach['mensagem'])[:80]}...")
    print()


def main():
    print("\n" + "=" * 60)
    print("  VIGIL SUMMIT - AUTONOMOUS B2B FUNNEL AGENT")
    print("  Powered by Vigil.AI + Agno + Claude 3.5 Sonnet")
    print("=" * 60)

    init_db()

    for lead_data in MOCK_LEADS:
        name_key = lead_data["name"].strip()
        context = EVENT_CONTEXTS[name_key]
        execute_full_flow(lead_data, context)

    print(f"\n{'='*60}")
    print("  TOKEN USAGE / COST REPORT")
    print(f"{'='*60}")
    records = list_usage()
    total_tokens = 0
    total_cost = 0.0
    for r in records:
        total_tokens += r["total_tokens"]
        total_cost += r["cost"] or 0.0
        print(
            f"  [{r['phase']}] {r['description']}\n"
            f"    Agent: {r['agent_name']} | Model: {r['model']}\n"
            f"    Tokens: {r['input_tokens']} in / {r['output_tokens']} out / {r['total_tokens']} total\n"
            f"    Cost: ${r['cost'] or 0:.6f} | Duration: {r['duration_seconds'] or 0:.2f}s\n"
            f"    Lead ID: {r['lead_id'] or '-'}"
        )
        print()
    print(f"  TOTAL: {total_tokens} tokens | ${total_cost:.6f}")
    print(f"{'='*60}")
    print("\n✓ Demonstration completed successfully!")


if __name__ == "__main__":
    main()
