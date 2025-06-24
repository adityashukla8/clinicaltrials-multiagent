from flows.full_trial_match import create_workflow
from tools.appwrite_write_trial_info import insert_match_to_appwrite

import json
import logging

from ipdb import set_trace as ipdb

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def match_trials(patient_id):
    app = create_workflow()
    initial_state = {
        "patient_id": patient_id
    }
    final_state = app.invoke(initial_state)

    for match in final_state['results']:
        # ipdb()
        insert_match_to_appwrite(match, patient_id)
        logger.info(f"Inserted match info for trial {match['trial_id']} & patient {patient_id} into Appwrite")

    return final_state['results']

if __name__ == "__main__":
    patient_id = 'P123'
    results = match_trials(patient_id)
    # ipdb()
    print(json.dumps(results, indent=2))
    logger.info("Trial matching completed successfully.")