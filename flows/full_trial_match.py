import logging
from langgraph.graph import StateGraph, END
from agents.patient_agent import get_patient_info_tool
from agents.trial_discovery_agent import return_trial_info_tool
from agents.eligibility_agent import evaluate_trials_llm
from agents.clinical_trials_summary_agent import get_trial_summary_card
from typing import TypedDict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrialMatch(TypedDict):
    trial_id: str
    match_criteria: str
    reason: str

class AgentState(TypedDict):
    patient_id: str
    patient_info: dict
    trials: List[dict]
    results: List[TrialMatch]

def filter_matched_trials(state):
    matched = [t for t in state["results"] if t.get("match_criteria") == "match"]
    if matched:
        return "generate_summary_cards"
    else:
        return "skip_summary_cards"

def summary_card_agent(state):
    matched = [t for t in state["results"] if t["match_criteria"] == "match"]
    for trial in matched:
        trial["summary_card"] = get_trial_summary_card(trial["trial_id"])
    return {"results": state["results"]}

def skip_summary_cards(state):
    return state  

def create_workflow():
    logger.info("Initializing workflow creation.")
    workflow = StateGraph(AgentState)
    workflow.add_node("get_patient_info", get_patient_info_tool)
    workflow.add_node("fetch_trials", return_trial_info_tool)
    workflow.add_node("llm_evaluation", evaluate_trials_llm)
    workflow.add_node("generate_summary_cards", summary_card_agent)
    workflow.add_node("skip_summary_cards", skip_summary_cards)

    workflow.set_entry_point("get_patient_info")
    workflow.add_edge("get_patient_info", "fetch_trials")
    workflow.add_edge("fetch_trials", "llm_evaluation")
    workflow.add_conditional_edges(
        "llm_evaluation",
        filter_matched_trials,
        {
            "generate_summary_cards": "generate_summary_cards",
            "skip_summary_cards": "skip_summary_cards"
        }
    )
    workflow.add_edge("generate_summary_cards", END)
    workflow.add_edge("skip_summary_cards", END)
    
    logger.info("Compiling workflow.")
    compiled_workflow = workflow.compile()
    logger.info("Workflow compiled successfully.")
    return compiled_workflow
