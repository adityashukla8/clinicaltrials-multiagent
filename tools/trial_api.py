import requests
import logging
from datetime import datetime

from tools.appwrite_write_trial_info import insert_or_update_trial_to_appwrite

from ipdb import set_trace as ipdb

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def fetch_clinical_trial_data(search_expr, max_studies):
    base_url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.cond": search_expr,
        "query.term": "AREA[Phase](PHASE4 OR PHASE3)AND AREA[LocationCountry](United States)",
        "filter.overallStatus": "RECRUITING",
        "pageSize": max_studies
    }

    trials = []
    studies_fetched = 0

    while True:
        response = requests.get(base_url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            studies = data.get('studies', [])
            for study in studies:
                try:
                    nct_id = study['protocolSection']['identificationModule'].get('nctId', 'Unknown')
                    title = study['protocolSection']['identificationModule'].get('officialTitle', 'No title')
                    eligibility = study['protocolSection']['eligibilityModule'].get('eligibilityCriteria', 'No eligibility info')
                    arms = study['protocolSection']['armsInterventionsModule'].get('armGroupList', {}).get('armGroup', [])
                    interventions = study['protocolSection']['armsInterventionsModule'].get('interventionList', {}).get('intervention', [])

                    trial_data = {
                        "trial_id": nct_id,
                        "title": title,
                        "eligibility": eligibility,
                        "arms": str(arms),
                        "interventions": str(interventions),
                        "summary_card": str({}),
                        "optimized_protocol": "",
                        "source_url": f"https://clinicaltrials.gov/ct2/show/{nct_id}",
                        "created_at": datetime.utcnow().isoformat()
                    }

                    ipdb()
                    insert_or_update_trial_to_appwrite(trial_data)
                    logger.info(f"Trial written to DB: {nct_id}")

                    trials.append(trial_data)
                    studies_fetched += 1

                    if studies_fetched >= max_studies:
                        break
                except Exception as e:
                    logger.warning(f"Skipping trial due to parsing error: {e}")
                    continue

            if not data.get('nextPageToken'):
                break
            params['pageToken'] = data['nextPageToken']
        else:
            logger.error(f"Failed to fetch data. Status code: {response.status_code}")
            break

    # ipdb()
    return trials
