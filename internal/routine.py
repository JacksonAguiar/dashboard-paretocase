import json
from datetime import datetime, timedelta
from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler()

AVAILABLE_TIMES = [9, 14, 20]

ROUTINE_TYPES = {
    "no_confirmation": {
        "event_type": "confirmation",
        "offset": timedelta(days=-1),
        "default_hour": None,
        "description": "No-confirmation: 1 day before event",
    },
    "engagement": {
        "event_type": "followup",
        "offset": timedelta(days=-3),
        "default_hour": None,
        "description": "Engagement: 3 days before event",
    },
    "engagement_confirmed": {
        "event_type": "followup",
        "offset": timedelta(hours=-2),
        "default_hour": None,
        "description": "Engagement: 2 hours before event (no-confirmation confirmed leads)",
    },
    "post_event_followup": {
        "event_type": "followup",
        "offset": timedelta(days=1),
        "default_hour": 0,
        "description": "Post-event follow-up: midnight after event (confirmed leads)",
    },
}


def _build_run_date(event_date: datetime, offset: timedelta, hour: int | None) -> datetime:
    run_date = event_date + offset
    if hour is not None:
        run_date = run_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    return run_date


def schedule_once(func: Callable, run_at: datetime, job_id: str, args: dict = None):
    args_list = [json.dumps(args)] if args else []
    scheduler.add_job(func, trigger=DateTrigger(run_date=run_at), id=job_id, replace_existing=True, args=args_list)


def update_routine_args(job_id: str, new_args: dict, merge: bool = True) -> bool:
    job = scheduler.get_job(job_id)
    if job is None:
        return False
    if merge and job.args:
        try:
            current = json.loads(job.args[0])
        except (IndexError, json.JSONDecodeError):
            current = {}
        current.update(new_args)
        updated = current
    else:
        updated = new_args
    scheduler.modify_job(job_id, args=[json.dumps(updated)])
    return True


def setup_event_routines(event_date: datetime):
    from workflows import (
        routine_no_confirmation,
        routine_engagement,
        routine_engagement_confirmed,
        routine_post_event_followup,
    )

    post_event_midnight = (event_date + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    schedule_once(
        routine_post_event_followup,
        post_event_midnight,
        "evt_post_event_followup",
    )

    for hour in AVAILABLE_TIMES:
        session_dt = event_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        suffix = f"{hour:02d}"

        no_conf = ROUTINE_TYPES["no_confirmation"]
        schedule_once(
            routine_no_confirmation,
            _build_run_date(session_dt, no_conf["offset"], no_conf["default_hour"]),
            f"evt_no_confirmation_{suffix}",
        )

        eng = ROUTINE_TYPES["engagement"]
        schedule_once(
            routine_engagement,
            _build_run_date(session_dt, eng["offset"], eng["default_hour"]),
            f"evt_engagement_{suffix}",
        )

        eng_conf = ROUTINE_TYPES["engagement_confirmed"]
        schedule_once(
            routine_engagement_confirmed,
            _build_run_date(session_dt, eng_conf["offset"], eng_conf["default_hour"]),
            f"evt_engagement_confirmed_{suffix}",
        )


def _purge_expired_leads_job():
    from database import purge_expired_leads
    purge_expired_leads()


def start():
    scheduler.add_job(
        _purge_expired_leads_job,
        trigger=IntervalTrigger(hours=24),
        id="lgpd_purge_expired_leads",
        replace_existing=True,
    )
    scheduler.start()


def stop():
    if scheduler.running:
        scheduler.shutdown(wait=False)
