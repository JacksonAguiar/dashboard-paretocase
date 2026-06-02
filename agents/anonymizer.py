import json

_PII_TAGS = {
    "name": "{{LEAD_NAME}}",
    "company": "{{LEAD_COMPANY}}",
}


def get_mapping(lead_data: dict) -> dict:
    return {
        tag: lead_data[field]
        for field, tag in _PII_TAGS.items()
        if lead_data.get(field) and isinstance(lead_data[field], str)
    }


def anonymize_lead(lead_data: dict) -> tuple[dict, dict]:
    mapping = get_mapping(lead_data)
    serialized = json.dumps(lead_data, ensure_ascii=False)
    for tag, value in sorted(mapping.items(), key=lambda x: len(x[1]), reverse=True):
        serialized = serialized.replace(value, tag)
    return json.loads(serialized), mapping


def deanonymize(text: str, mapping: dict) -> str:
    for tag, value in mapping.items():
        text = text.replace(tag, value)
    return text
