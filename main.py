from dotenv import load_dotenv

load_dotenv()

from database import init_db, save_lead, list_usage
from agents.single_workflow import run_direct_workflow
from tools import search_professional_data
import json

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


def main():
    print("\n" + "=" * 60)
    print("  VIGIL SUMMIT - AUTONOMOUS B2B FUNNEL AGENT")
    print("=" * 60)

    init_db()

    lead_data = MOCK_LEADS[0]
    base_keys = {"name", "email", "company", "title"}
    enriched_data = json.loads(search_professional_data(lead_data["email"], lead_data["company"]))

    lead_id = save_lead(
        name=lead_data["name"].strip(),
        email=lead_data["email"].strip(),
        company=lead_data["company"].strip(),
        title=lead_data["title"],
        additional_data={k: v for k, v in lead_data.items() if k not in base_keys},
        enriched_data=enriched_data,
    )
    print(f"[TEST] Lead saved with ID {lead_id}")

    run_direct_workflow(lead_id)

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


if __name__ == "__main__":
    main()
