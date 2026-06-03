from agno.models.anthropic import Claude
import os

def get_claude_haiku_model():
    name = os.getenv("FALLBACK_AGENT_NAME")
    if not name:
        raise ValueError("FALLBACK_AGENT_NAME not set in environment")
    return Claude(id=name, api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_claude_sonnet_model():
    name = os.getenv("MAIN_AGENT_NAME")
    if not name:
        raise ValueError("MAIN_AGENT_NAME not set in environment")
    return Claude(id=name, api_key=os.getenv("ANTHROPIC_API_KEY"))
