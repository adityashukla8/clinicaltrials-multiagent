from flows.full_trial_match import create_workflow
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(patient_id):
    app = create_workflow()
    initial_state = {
        "patient_id": patient_id
    }
    final_state = app.invoke(initial_state)
    return final_state['results']

if __name__ == "__main__":
    patient_id = 'P123'
    results = main(patient_id)
    print(json.dumps(results, indent=2))
    logger.info("Trial matching completed successfully.")