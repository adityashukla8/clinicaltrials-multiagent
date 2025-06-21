from langgraph.graph import StateGraph, END
from agents.patient_agent import get_patient_info_tool
from agents.trial_discovery_agent import return_trial_info_tool
from agents.eligibility_agent import evaluate_trials_llm
from typing import TypedDict, List

class TrialMatch(TypedDict):
    trial_id: str
    match_criteria: str
    reason: str

class AgentState(TypedDict):
    patient_id: str
    patient_info: dict
    trials: List[dict]
    results: List[TrialMatch]

def create_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("get_patient_info", get_patient_info_tool)
    workflow.add_node("fetch_trials", return_trial_info_tool)
    workflow.add_node("llm_evaluation", evaluate_trials_llm)

    workflow.set_entry_point("get_patient_info")
    workflow.add_edge("get_patient_info", "fetch_trials")
    workflow.add_edge("fetch_trials", "llm_evaluation")
    workflow.add_edge("llm_evaluation", END)
    
    return workflow.compile()
