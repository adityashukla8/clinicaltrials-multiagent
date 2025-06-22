import logging
from tools.trial_api import fetch_clinical_trial_data

logger = logging.getLogger(__name__)

def return_trial_info_tool(state):
    patient = state["patient_info"]
    logger.info(f"Fetching clinical trial data for diagnosis: {patient.get('diagnosis')}")
    
    critlist, nctidlist = fetch_clinical_trial_data(patient["diagnosis"], 10)
    trials = [{"trial_id": tid, "criteria": crit} for tid, crit in zip(nctidlist, critlist)]
    state["trials"] = trials
    return state
