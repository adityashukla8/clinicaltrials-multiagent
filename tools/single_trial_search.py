import requests
import logging
import json 

from ipdb import set_trace as ipdb

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def fetch_trial_details_by_nct_id(nct_id):
    base_url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"

    try:
        response = requests.get(base_url, timeout=60)
        if response.status_code != 200:
            logger.error(f"Failed to fetch trial {nct_id}. Status code: {response.status_code}")
            return None

        study = response.json()

        # Shortcut to section
        protocol = study.get("protocolSection", {})

        return {
            "trial_id": nct_id,
            "title": protocol.get("identificationModule", {}).get("officialTitle", "N/A"),
            "status": protocol.get("statusModule", {}).get("overallStatus", "N/A"),
            "phases": protocol.get("designModule", {}).get("phaseList", {}).get("phases", []),
            "conditions": protocol.get("conditionsModule", {}).get("conditions", []),
            "interventions": protocol.get("armsInterventionsModule", {}).get("interventions", []),
            "eligibility_criteria": protocol.get("eligibilityModule", {}).get("eligibilityCriteria", "N/A"),
            "gender": protocol.get("eligibilityModule", {}).get("sex", "All"),
            "minimum_age": protocol.get("eligibilityModule", {}).get("minimumAge", "N/A"),
            "maximum_age": protocol.get("eligibilityModule", {}).get("maximumAge", "N/A"),
            "locations": protocol.get("contactsLocationsModule", {}).get("locations", []),
        }

    except Exception as e:
        logger.error(f"Exception occurred while fetching trial {nct_id}: {e}")
        return None

# if __name__ == "__main__":
#     nct_id = "NCT06750094"  # Example NCT ID
#     trial_details = fetch_trial_details_by_nct_id(nct_id)
#     if trial_details:
#         print(f"Details for trial {nct_id}:")
#         # print with indent
#         print(json.dumps(trial_details, indent=2))
    
#         ipdb()
#     else:
#         print(f"No details found for trial {nct_id}.")