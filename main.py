import json
from database import init_db, get_lead, list_usage
from workflows import phase_1_capture, phase_2_enrichment, phase_3_engagement, phase_4_followup

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


def execute_full_flow(lead_data: dict, event_context: str):
    lead_id = phase_1_capture(lead_data)
    phase_2_enrichment(lead_id)
    phase_3_engagement(lead_id)
    phase_4_followup(lead_id, event_context)

    final_lead = get_lead(lead_id)
    print(f"\n{'#'*60}")
    print(f"FINAL SUMMARY - {final_lead['name']}")
    print(f"{'#'*60}")
    print(f"  Status: {final_lead['funnel_status']}")
    print(f"  Enriched data: {json.dumps(final_lead['enriched_data'], indent=2, ensure_ascii=False)}")
    print(f"  Total interactions: {len(final_lead['interaction_history'])}")
    for i, interaction in enumerate(final_lead["interaction_history"], 1):
        print(f"    {i}. [{interaction['type']}] {interaction['content'][:80]}...")
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
