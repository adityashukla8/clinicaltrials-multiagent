from flows.protocol_optimization_workflow import create_protocol_optimization_workflow
from tools.single_trial_search import fetch_trial_details_by_nct_id
from tools.appwrite_get_all_patients import fetch_all_patients

from ipdb import set_trace as ipdb

def run_protocol_optimization(trial_id):
    app = create_protocol_optimization_workflow()
    trial_info = fetch_trial_details_by_nct_id(trial_id)
    patients_info_list = fetch_all_patients()

    initial_state = {
        "trial_id": trial_id,
        "trial_info": trial_info,
        "patients_info_list": patients_info_list
    }

    final_state = app.invoke(initial_state)

    return final_state

# ipdb()