from langgraph.graph import StateGraph, END

from agents.protocol_optimization_age_agent import age_optimization_agent
from agents.protocol_optimization_biomarker_agent import biomarker_optimization_agent
from agents.protocol_optimization_summary_agent import protocol_optimization_summary

from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    trial_id: str
    trial_info: Dict[str, Any]
    patients_info_list: List[Dict[str, Any]]
    age_optimization_result: Optional[Dict[str, Any]]
    biomarker_optimization_result: Optional[Dict[str, Any]]
    supervisor_summary: Optional[Dict[str, Any]]

def create_protocol_optimization_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("age_optimization_agent", age_optimization_agent)
    workflow.add_node("biomarker_optimization_agent", biomarker_optimization_agent)
    workflow.add_node("protocol_optimization_summary_agent", protocol_optimization_summary)

    workflow.set_entry_point("age_optimization_agent")
    workflow.add_edge("age_optimization_agent", "biomarker_optimization_agent")
    workflow.add_edge("biomarker_optimization_agent", "protocol_optimization_summary_agent")
    workflow.set_finish_point("protocol_optimization_summary_agent")

    return workflow.compile()
