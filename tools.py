import time
import random
import json
from database import get_lead

_INTERNAL_DATA = json.load(open("MANUAL_DATA.json"))
_WEB_SCRAPING = json.load(open("WEB_SCRAPING.json"))

MOCK_LEAD_RESPONSES = [
    "Obrigado pela mensagem! Vou sim participar do evento.",
    "Muito interessante, pode me enviar mais detalhes?",
    "Confirmo presença! Estou curioso sobre a demo de threat detection.",
    "Agradeço o contato. Vou avaliar internamente com meu time.",
    "Perfeito, já marquei na agenda. Até lá!",
]

_ROLE_KEYWORDS: dict[str, list[str]] = {
    "ciso": ["ciso", "chief information security", "vp security", "head of security", "information security officer", "vp of security"],
    "cto": ["cto", "chief technology", "chief technical", "director of technology", "vp engineering", "vp of engineering", "head of engineering"],
    "it_director": ["it director", "director of it", "head of it", "director of information technology", "diretor de ti", "diretor de tecnologia"],
    "compliance_officer": ["compliance", "risk officer", "chief compliance", "head of compliance", "grc", "officer de risco"],
    "data_protection_officer": ["data protection officer", "privacy officer", "dpo", "encarregado de dados", "chief privacy"],
    "devops_lead": ["devops", "sre", "site reliability", "platform engineer", "infrastructure lead", "devsecops", "cloud engineer lead"],
    "security_manager": ["security operations manager", "soc manager", "head of soc", "security manager", "gestor de segurança", "gerente de segurança"],
    "soc_analyst": ["soc analyst", "tier 2", "tier 3", "threat analyst", "incident response analyst", "analista soc", "threat hunter"],
    "network_admin": ["network admin", "network engineer", "network administrator", "administrador de rede", "engenheiro de redes"],
    "analyst": ["analyst", "security analyst", "information security analyst", "cybersecurity analyst", "analista de segurança", "analista de cibersegurança"],
}


def _detect_role(email: str, title: str) -> str:
    combined = f"{email} {title}".lower()
    for role, keywords in _ROLE_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return role
    return "analyst"


def search_professional_data(email: str, company: str, title: str = "") -> str:
    """Search enriched professional data for a lead from email, company and job title.

    Args:
        email: Professional email of the lead.
        company: Company name of the lead.
        title: Job title of the lead (optional but improves role detection accuracy).
    """
    time.sleep(0.5)

    role = _detect_role(email, title)

    internal_profile = _INTERNAL_DATA["profiles"].get(role, _INTERNAL_DATA["profiles"]["analyst"])
    web_data = _WEB_SCRAPING.get(role, {})

    actual_title = title if title else internal_profile.get("actual_title", "")
    sector = _infer_sector(company, internal_profile.get("typical_sectors", []))
    company_size = internal_profile.get("typical_company_size", "")

    sector_context = _INTERNAL_DATA["categories"]["sector"].get(sector, {})
    size_context = _INTERNAL_DATA["categories"]["company_size"].get(company_size, {})

    icp_score = internal_profile.get("icp_score", 50)
    icp_tier = _get_icp_tier(icp_score)
    icp_guidance = _INTERNAL_DATA["icp_scoring"].get(icp_tier, {})

    enriched = {
        "verified_email": email,
        "verified_company": company,
        "detected_role_key": role,
        "profile": {
            "actual_title": actual_title,
            "level": internal_profile.get("level"),
            "decision_role": internal_profile.get("decision_role"),
            "sector": sector,
            "company_size": company_size,
            "technologies_used": internal_profile.get("technologies_used", []),
            "icp_score": icp_score,
            "icp_tier": icp_guidance.get("label"),
            "recommended_channel": icp_guidance.get("channel"),
            "recommended_actions": icp_guidance.get("recommended_actions", []),
        },
        "persona_intelligence": {
            "concerns": internal_profile.get("concerns", []),
            "pain_points": internal_profile.get("pain_points", []),
            "approach": internal_profile.get("approach"),
            "messaging_tone": internal_profile.get("messaging_tone"),
            "key_metrics": internal_profile.get("key_metrics", []),
            "common_objections": internal_profile.get("objections", []),
            "objection_handling": internal_profile.get("objection_handling"),
        },
        "sector_context": {
            "characteristics": sector_context.get("characteristics"),
            "icp_approach": sector_context.get("icp_approach"),
            "sector_concerns": sector_context.get("concerns", []),
            "use_cases": sector_context.get("use_cases", []),
        },
        "company_size_context": {
            "description": size_context.get("description"),
            "icp_approach": size_context.get("icp_approach"),
            "pain_points": size_context.get("pain_points", []),
            "decision_factors": size_context.get("decision_factors", []),
        },
        "web_scraping": {
            "source": "simulated — replace with real scraping pipeline",
            "linkedin": web_data.get("linkedin", {}),
            "news": web_data.get("news", []),
            "posts": web_data.get("posts", []),
        },
    }
    return json.dumps(enriched, ensure_ascii=False)


def _infer_sector(company: str, typical_sectors: list[str]) -> str:
    company_lower = company.lower()
    sector_hints = {
        "bank": "Financial / Banking",
        "banco": "Financial / Banking",
        "financ": "Financial / Banking",
        "fintech": "Financial / Fintech",
        "pagament": "Financial / Fintech",
        "hospital": "Healthcare",
        "saude": "Healthcare",
        "health": "Healthcare",
        "clinic": "Healthcare",
        "manufactur": "Manufacturing",
        "industri": "Manufacturing",
        "fabrica": "Manufacturing",
        "retail": "Retail / E-commerce",
        "varejo": "Retail / E-commerce",
        "loja": "Retail / E-commerce",
        "ecommerce": "Retail / E-commerce",
        "universidade": "Education",
        "university": "Education",
        "faculdade": "Education",
        "escola": "Education",
        "gov": "Government / Public Sector",
        "federal": "Government / Public Sector",
        "municipal": "Government / Public Sector",
        "legal": "Legal / Consulting",
        "advogad": "Legal / Consulting",
        "consultoria": "Legal / Consulting",
        "law": "Legal / Consulting",
        "cloud": "Technology / Cloud Services",
        "saas": "Technology / SaaS",
        "tech": "Technology / Cybersecurity",
        "cyber": "Technology / Cybersecurity",
        "security": "Technology / Cybersecurity",
        "seguranca": "Technology / Cybersecurity",
    }
    for hint, sector in sector_hints.items():
        if hint in company_lower:
            return sector
    return typical_sectors[0] if typical_sectors else "Technology / Cybersecurity"


def _get_icp_tier(score: int) -> str:
    if score >= 80:
        return "tier_a"
    if score >= 50:
        return "tier_b"
    return "tier_c"


def send_message(lead_id: int, channel: str, message: str) -> str:
    """Send a message to the lead via specified channel and return simulated response.

    Args:
        lead_id: ID of the lead in the database.
        channel: Communication channel (email or whatsapp).
        message: Content of the message to be sent.
    """
    time.sleep(0.3)

    lead = get_lead(lead_id)
    if lead is None:
        return json.dumps({"error": f"Lead {lead_id} not found"})

    lead_response = random.choice(MOCK_LEAD_RESPONSES)

    result = {
        "status": "sent",
        "channel": channel,
        "recipient": lead["name"],
        "lead_response": lead_response,
    }
    return json.dumps(result, ensure_ascii=False)


def schedule_meeting(lead_id: int, datetime: str) -> str:
    """Schedule a commercial meeting with the lead.

    Args:
        lead_id: ID of the lead in the database.
        datetime: Date and time of the meeting in 'YYYY-MM-DD HH:MM' format.
    """
    time.sleep(0.3)

    lead = get_lead(lead_id)
    if lead is None:
        return json.dumps({"error": f"Lead {lead_id} not found"})

    result = {
        "status": "scheduled",
        "lead": lead["name"],
        "company": lead["company"],
        "datetime": datetime,
        "meeting_link": f"https://meet.vigil.ai/demo-{lead_id}",
    }
    return json.dumps(result, ensure_ascii=False)
