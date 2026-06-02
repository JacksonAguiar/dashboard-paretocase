import sqlite3
import json
import os
from datetime import datetime, timedelta, timezone

DB_PATH = "leads.db"

LEAD_TTL_DAYS = int(os.getenv("LEAD_TTL_DAYS", "180"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            company TEXT,
            title TEXT,
            funnel_status TEXT DEFAULT 'captured',
            enriched_data TEXT DEFAULT '{}',
            additional_data TEXT DEFAULT '{}',
            channel TEXT,
            planner_result TEXT,
            followup_instructions TEXT,
            user_code TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT
        )
    """)
    try:
        conn.execute("ALTER TABLE leads ADD COLUMN expires_at TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE leads ADD COLUMN channel TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE leads ADD COLUMN planner_result TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE leads ADD COLUMN followup_instructions TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE leads ADD COLUMN user_code TEXT")
    except sqlite3.OperationalError:
        pass
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            agent_name TEXT NOT NULL,
            phase TEXT NOT NULL,
            description TEXT NOT NULL,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            cost REAL,
            duration_seconds REAL,
            model TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS funil_approchs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            approuch TEXT NOT NULL,
            mensagem TEXT,
            channel TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_funil_approch(user_id: int, approuch: str, mensagem: str, channel: str | None = None) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO funil_approchs (user_id, approuch, mensagem, channel) VALUES (?, ?, ?, ?)",
        (user_id, approuch, mensagem, channel),
    )
    conn.commit()
    approch_id = cursor.lastrowid
    conn.close()
    return approch_id


def list_funil_approchs(user_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM funil_approchs WHERE user_id = ? ORDER BY created_at",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_lead(name: str, email: str, company: str, title: str, additional_data: dict | None = None, channel: str | None = None, user_code: str | None = None) -> int:
    conn = get_connection()
    expires_at = (datetime.now(timezone.utc) + timedelta(days=LEAD_TTL_DAYS)).isoformat()
    cursor = conn.execute(
        "INSERT INTO leads (name, email, company, title, additional_data, channel, user_code, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, email, company, title, json.dumps(additional_data or {}, ensure_ascii=False), channel, user_code, expires_at),
    )
    conn.commit()
    lead_id = cursor.lastrowid
    conn.close()
    return lead_id


def purge_expired_leads() -> int:
    conn = get_connection()
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "DELETE FROM leads WHERE expires_at IS NOT NULL AND expires_at < ?",
        (now,),
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted


def get_lead(lead_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    lead = dict(row)
    lead["enriched_data"] = json.loads(lead["enriched_data"])
    lead["additional_data"] = json.loads(lead["additional_data"])
    lead["planner_result"] = json.loads(lead["planner_result"]) if lead.get("planner_result") else None
    return lead


def get_lead_by_email(email: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM leads WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row is None:
        return None
    lead = dict(row)
    lead["enriched_data"] = json.loads(lead["enriched_data"])
    lead["additional_data"] = json.loads(lead["additional_data"])
    lead["planner_result"] = json.loads(lead["planner_result"]) if lead.get("planner_result") else None
    return lead


def get_lead_by_user_code(user_code: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM leads WHERE user_code = ?", (user_code,)).fetchone()
    conn.close()
    if row is None:
        return None
    lead = dict(row)
    lead["enriched_data"] = json.loads(lead["enriched_data"])
    lead["additional_data"] = json.loads(lead["additional_data"])
    lead["planner_result"] = json.loads(lead["planner_result"]) if lead.get("planner_result") else None
    return lead


def append_additional_event(lead_id: int, event_type: str, content: str):
    lead = get_lead(lead_id)
    if lead is None:
        return
    data = lead["additional_data"]
    events = data.get("events", [])
    events.append({"event_type": event_type, "content": content, "timestamp": datetime.now().isoformat()})
    data["events"] = events
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET additional_data = ? WHERE id = ?",
        (json.dumps(data, ensure_ascii=False), lead_id),
    )
    conn.commit()
    conn.close()


UPDATABLE_FIELDS = {"name", "email", "company", "title", "channel", "funnel_status", "user_code"}


def update_lead(lead_id: int, **kwargs) -> bool:
    fields = {k: v for k, v in kwargs.items() if k in UPDATABLE_FIELDS}
    if not fields:
        return False
    set_clause = ", ".join(f"{col} = ?" for col in fields)
    values = list(fields.values()) + [lead_id]
    conn = get_connection()
    cursor = conn.execute(f"UPDATE leads SET {set_clause} WHERE id = ?", values)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def update_status(lead_id: int, new_status: str):
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET funnel_status = ? WHERE id = ?",
        (new_status, lead_id),
    )
    conn.commit()
    conn.close()


def update_channel(lead_id: int, channel: str):
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET channel = ? WHERE id = ?",
        (channel, lead_id),
    )
    conn.commit()
    conn.close()


def update_planner_result(lead_id: int, result):
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET planner_result = ? WHERE id = ?",
        (json.dumps(result, ensure_ascii=False) if result is not None else None, lead_id),
    )
    conn.commit()
    conn.close()


def update_followup_instructions(lead_id: int, instructions: str):
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET followup_instructions = ? WHERE id = ?",
        (instructions, lead_id),
    )
    conn.commit()
    conn.close()


def update_enriched_data(lead_id: int, data: dict):
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET enriched_data = ? WHERE id = ?",
        (json.dumps(data, ensure_ascii=False), lead_id),
    )
    conn.commit()
    conn.close()


def update_additional_data(lead_id: int, data: dict):
    lead = get_lead(lead_id)
    if lead is None:
        return
    current = lead["additional_data"]
    current.update(data)
    conn = get_connection()
    conn.execute(
        "UPDATE leads SET additional_data = ? WHERE id = ?",
        (json.dumps(current, ensure_ascii=False), lead_id),
    )
    conn.commit()
    conn.close()


def register_usage(response, agent_name: str, phase: str, description: str, lead_id: int | None = None):
    metrics = response.metrics
    conn = get_connection()
    conn.execute(
        """INSERT INTO agent_usage
           (lead_id, agent_name, phase, description, input_tokens, output_tokens, total_tokens, cost, duration_seconds, model)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            lead_id,
            agent_name,
            phase,
            description,
            getattr(metrics, "input_tokens", 0),
            getattr(metrics, "output_tokens", 0),
            getattr(metrics, "total_tokens", 0),
            getattr(metrics, "cost", None),
            getattr(metrics, "duration", None),
            response.model or "",
        ),
    )
    conn.commit()
    conn.close()


def list_usage() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM agent_usage ORDER BY created_at").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def list_leads_by_status(status: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM leads WHERE funnel_status = ?", (status,)).fetchall()
    conn.close()
    leads = []
    for row in rows:
        lead = dict(row)
        lead["enriched_data"] = json.loads(lead["enriched_data"])
        lead["additional_data"] = json.loads(lead["additional_data"])
        lead["planner_result"] = json.loads(lead["planner_result"]) if lead.get("planner_result") else None
        leads.append(lead)
    return leads
