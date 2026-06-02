import json

from agents import planner_agent as planner_module
from agents import writer_agent as writer_module
from agents import followup_agent as followup_module
from services import lead_service


def run_direct_workflow(lead_id: int):
    lead_data = lead_service.get_lead_by_id(lead_id)
    if lead_data is None:
        return

    planner_output_str = planner_module.run_agent(
        input_data=json.dumps(lead_data, ensure_ascii=False),
        lead_id=lead_id,
    )
    planner_output = json.loads(planner_output_str)
    channel = planner_output.get("analyse", {}).get("contact_channel", "email")

    engajamento = planner_output.get("engajamento-1", {})
    if engajamento.get("content_writer"):
        writer_module.run_agent(
            dispatch=False,
            input_data=engajamento["content_writer"],
            channel=channel,
            lead_id=lead_id,
            _event="engajamento-1",
        )

    checkin = planner_output.get("check-in", {})
    if checkin.get("content_writer"):
        writer_module.run_agent(
            dispatch=False,
            input_data=checkin["content_writer"],
            channel=channel,
            lead_id=lead_id,
            _event="check-in",
        )

    followup_input = {**lead_data, "planner_result": planner_output}
    followup_result = followup_module.run_followup_agent(
        dispatch=False,
        input_data=json.dumps(followup_input, ensure_ascii=False),
        lead_id=lead_id,
        channel=channel,
    )

    followup_content = json.loads(followup_result.content)
    for routine in followup_content.get("routines", []):
        writer_module.run_agent(
            dispatch=False,
            input_data=routine.get("content_writer"),
            channel=routine.get("channel", channel),
            lead_id=lead_id,
            _event=routine.get("name", "follow-up"),
        )