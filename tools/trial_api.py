import requests
import logging

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

    eligibility_criteria = []
    nct_ids = []
    studies_fetched = 0

    while True:
        response = requests.get(base_url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            studies = data.get('studies', [])
            for study in studies:
                nct_id = study['protocolSection']['identificationModule'].get('nctId', 'Unknown')
                eligibility_criteria_text = study['protocolSection']['eligibilityModule'].get('eligibilityCriteria', 'Unknown')
                eligibility_criteria.append(eligibility_criteria_text)
                nct_ids.append(nct_id)
                studies_fetched += 1
                if studies_fetched >= max_studies:
                    break
            if not data.get('nextPageToken'): break
            params['pageToken'] = data['nextPageToken']
        else:
            logger.error(f"Failed to fetch data. Status code: {response.status_code}")
            break

    return eligibility_criteria, nct_ids
