import logging
from tools.trial_api import fetch_clinical_trial_data

logger = logging.getLogger(__name__)

def return_trial_info_tool(state):
    patient = state["patient_info"]
    logger.info(f"Fetching clinical trial data for diagnosis: {patient.get('diagnosis')}")

    trial_list = fetch_clinical_trial_data(patient["diagnosis"], max_studies=10)
    trials = [{"trial_id": t["trial_id"], "criteria": t["eligibility"]} for t in trial_list]

    state["trials"] = trials
    return state