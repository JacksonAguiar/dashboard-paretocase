import os
import random
import string
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

from agents.single_workflow import run_direct_workflow
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    from internal.routine import start, stop, setup_event_routines
    start()
    event_date_str = os.getenv("EVENT_DATE")
    if event_date_str:
        setup_event_routines(datetime.fromisoformat(event_date_str))
    yield
    stop()


app = FastAPI(lifespan=lifespan)
_bearer = HTTPBearer()


def _require_auth(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
    try:
        jwt.decode(credentials.credentials, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


class LoginRequest(BaseModel):
    email: str
    password: str


class SubscribeRequest(BaseModel):
    name: str
    email: str
    company: str
    title: str
    channel: str | None = None
    additional_data: dict | None = None


@app.post("/auth/login")
def login(body: LoginRequest):
    if body.email != os.getenv("AUTH_EMAIL") or body.password != os.getenv("AUTH_PASSWORD"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = jwt.encode(
        {"sub": body.email, "exp": datetime.now(timezone.utc) + timedelta(hours=24)},
        os.getenv("JWT_SECRET"),
        algorithm="HS256",
    )
    return {"token": token}


def _run_planner(lead_id: int):
    import json
    from agents.planner_agent import planner_agent
    from database import get_lead, update_planner_result, register_usage

    lead = get_lead(lead_id)
    if lead is None:
        return

    prompt = (
        f"Elabore o plano de abordagem para o seguinte lead do Vigil Summit:\n\n"
        f"- Nome: {lead['name']}\n"
        f"- Email: {lead['email']}\n"
        f"- Cargo: {lead['title']}\n"
        f"- Empresa: {lead['company']}\n"
        f"- Dados adicionais: {json.dumps(lead.get('additional_data') or {}, ensure_ascii=False)}\n"
    )

    response = planner_agent.run(prompt)
    register_usage(
        response,
        agent_name="Vigil Sales Strategist Agent",
        phase="phase_planner",
        description="Pre-event engagement plan",
        lead_id=lead_id,
    )
    update_planner_result(lead_id, response.content if isinstance(response.content, str) else json.dumps(response.content, ensure_ascii=False))


class AdditionalInfo(BaseModel):
    event_type: str
    content: str


class EventRequest(BaseModel):
    user_code: str
    additional_info: AdditionalInfo


@app.post("/event/lead")
def lead_event(body: EventRequest):
    from database import get_lead_by_user_code, append_additional_event

    lead = get_lead_by_user_code(body.user_code)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    append_additional_event(lead["id"], body.additional_info.event_type, body.additional_info.content)
    return {"lead_id": lead["id"], "event_type": body.additional_info.event_type}

@app.post("/subscribe/single-workflow", status_code=status.HTTP_201_CREATED)
def subscribe_single_workflow(body: SubscribeRequest, background_tasks: BackgroundTasks):
    import json
    import sqlite3
    from database import save_lead
    from tools import search_professional_data
    
    user_code = "".join(random.choices(string.ascii_letters + string.digits, k=10))

    enriched_data = json.loads(search_professional_data(body.email, body.company))

    try:
        lead_id = save_lead(
            name=body.name,
            email=body.email,
            company=body.company,
            title=body.title,
            additional_data=body.additional_data or {},
            user_code=user_code,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Lead already exists")

    from database import update_enriched_data
    update_enriched_data(lead_id, enriched_data)

    background_tasks.add_task(run_direct_workflow, lead_id)
    
    return {"lead_id": lead_id, "user_code": user_code}

@app.post("/subscribe", status_code=status.HTTP_201_CREATED)
def subscribe(body: SubscribeRequest, background_tasks: BackgroundTasks):
    import json
    import sqlite3
    from database import save_lead
    from tools import search_professional_data

    user_code = "".join(random.choices(string.ascii_letters + string.digits, k=10))

    enriched_data = json.loads(search_professional_data(body.email, body.company))

    try:
        lead_id = save_lead(
            name=body.name,
            email=body.email,
            company=body.company,
            title=body.title,
            additional_data=body.additional_data or {},
            user_code=user_code,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    from database import update_enriched_data
    update_enriched_data(lead_id, enriched_data)

    background_tasks.add_task(_run_planner, lead_id)

    return {"lead_id": lead_id, "user_code": user_code, "funnel_status": "captured"}


class FunilApprochRequest(BaseModel):
    user_id: int
    approuch: str
    mensagem: str
    channel: str | None = None


@app.post("/funil-approchs", status_code=status.HTTP_201_CREATED, dependencies=[Depends(_require_auth)])
def create_funil_approch_endpoint(body: FunilApprochRequest):
    from services.funil_approch_service import create_funil_approch

    return create_funil_approch(
        user_id=body.user_id,
        approuch=body.approuch,
        mensagem=body.mensagem,
        channel=body.channel,
    )


@app.get("/funil-approchs/{user_id}", dependencies=[Depends(_require_auth)])
def list_funil_approchs_endpoint(user_id: int):
    from services.funil_approch_service import get_funil_approchs

    return get_funil_approchs(user_id)


@app.patch("/leads/{lead_id}/confirm")
def confirm_participation(lead_id: int, late: bool = Query(default=False)):
    from database import get_lead, update_status

    if get_lead(lead_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    funnel_status = "late_confirmed" if late else "confirmed"
    update_status(lead_id, funnel_status)
    return {"lead_id": lead_id, "funnel_status": funnel_status}
