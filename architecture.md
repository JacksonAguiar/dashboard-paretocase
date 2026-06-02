# Vigil Summit — AI Funnel Agent

## Architecture Overview

```
main.py → workflows.py → agent.py → tools.py
                ↕                        ↕
            database.py ←────────────────┘
```

## Components

- **database.py** — SQLite CRUD. Table `leads` stores funnel status, enriched data (JSON), interaction history (JSON).
- **tools.py** — Mocked external integrations (LinkedIn enrichment, WhatsApp/Email send, meeting scheduler). Simulates latency and returns realistic structured data.
- **agent.py** — Agno Agent with Claude 3.5 Sonnet. System prompt defines a B2B SDR persona (Ana) specialized in cybersecurity.
- **workflows.py** — Orchestrates 4 funnel phases, each invoking the agent with context and letting it autonomously pick tools.
- **main.py** — Demo runner. Creates 2 leads and pushes them through the full funnel.

## Funnel Phases

```
[Captação] → [Enriquecimento] → [Engajamento] → [Follow-up]
  save lead    enrich via tool    ICP score →      post-event
  status:      status:            channel pick     propose meeting
  captado      enriquecido        status:          status:
                                  confirmado       reuniao_agendada
```

## Stack

| Layer | Tech |
|-------|------|
| Agent Framework | Agno |
| LLM | Claude 3.5 Sonnet (Anthropic) |
| Database | SQLite3 |
| Validation | Pydantic |

## Data Flow

1. Lead enters via `fase_1_captacao` → saved to DB with status `captado`
2. Agent calls `search_professional_data` → DB updated with enriched JSON, status → `enriquecido`
3. ICP score determines priority/channel → Agent drafts + sends personalized message → status → `confirmado`
4. Post-event: Agent sends follow-up + schedules meeting → status → `reuniao_agendada`

All interactions (sent/received) are appended to `historico_interacoes` JSON array in the DB.
