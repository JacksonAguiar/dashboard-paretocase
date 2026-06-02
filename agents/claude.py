from agno.models.anthropic import Claude
import os

def get_claude_haiku_model():
    return Claude(id=os.getenv("CLAUDE_FALLBACK_MODEL"), api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_claude_sonnet_model():
    return Claude(id=os.getenv("CLAUDE_MAIN_MODEL"), api_key=os.getenv("ANTHROPIC_API_KEY"))
