from ipdb import set_trace as ipdb

import json
import logging
import os
import requests
import re

from google import genai
from google.genai import types

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def clean_json_from_gemini(raw_text):
    # Remove triple backticks and optional "json"
    cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
    return json.loads(cleaned)


def get_patient_info():
    return {
        "age": 52,
        "diagnosis": "Cancer of the Uterine Cervix",
        "treatment_history": ["taxane-based chemotherapy"],
        "country": "USA",
        "gender": "Female"
    }

def fetch_clinical_trial_data(search_expr, max_studies):
    """
    Fetches clinical trial data from ClinicalTrials.gov API based on search criteria.
    
    Args:
        search_expr (str): Medical condition to search for
        max_studies (int): Maximum number of studies to retrieve
    
    Returns:
        tuple: (list of eligibility criteria, list of NCT IDs)
    """
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
        # Make API request with timeout
        response = requests.get(base_url, params=params, timeout=60)

        if response.status_code == 200:
            data = response.json()
            studies = data.get('studies', [])

            # Process each study in the response
            for study in studies:
                nct_id = study['protocolSection']['identificationModule'].get('nctId', 'Unknown')
                nct_ids.append(nct_id)

                eligibility_criteria_text = study['protocolSection']['eligibilityModule'].get('eligibilityCriteria', 'Unknown')
                eligibility_criteria.append(eligibility_criteria_text)

                studies_fetched += 1
                if studies_fetched >= max_studies:
                    break

            # Handle pagination
            nextPageToken = data.get('nextPageToken')
            if nextPageToken and studies_fetched < max_studies:
                params['pageToken'] = nextPageToken
            else:
                break
        else:
            logger.error(f"Failed to fetch data. Status code: {response.status_code}")
            break

    return eligibility_criteria, nct_ids


def return_trial_info(age, medicalCondition, gender, country):
    """
    Fetches clinical trial information based on patient criteria.
    
    Args:
        age (str): Patient age
        medicalCondition (str): Medical condition
        gender (str): Patient gender
        country (str): Patient country
    
    Returns:
        list: Contains eligibility criteria and NCT IDs
    """
    max_studies = 10
    search_expr = medicalCondition
    critlist, nctidlist = fetch_clinical_trial_data(search_expr, max_studies)
    loclientdict = [critlist, nctidlist]
    return loclientdict

def evaluate_eligibility_with_llm(patient_info, trial_criteria, trial_id, gemini_api_key):
    client = genai.Client(
        vertexai=True,
        project="ai-in-action-461412",
        location="global",
    )

    prompt = types.Part.from_text(text=f"""You are a clinical trials assistant. Determine if the following patient qualifies for the trial criteria.

PATIENT:
{json.dumps(patient_info, indent=2)}

TRIAL ID: {trial_id}
CRITERIA:
\"\"\"
{trial_criteria}
\"\"\"

Reply strictly in this JSON format:
{{
  "trial_id": "{trial_id}",
  "match_criteria": "match" or "not match",
  "reason": "brief explanation"
}}
    """
)

    model = "gemini-2.5-flash"
    contents = [
    types.Content(
        role="user",
        parts=[
        prompt
        ]
    )
    ]

    generate_content_config = types.GenerateContentConfig(
    temperature = 0.1,
    top_p = 1,
    seed = 0,
    max_output_tokens = 65535,
    safety_settings = [types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="OFF"
    ),types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="OFF"
    ),types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="OFF"
    ),types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="OFF"
    )],
    thinking_config=types.ThinkingConfig(
        thinking_budget=0,
    ),
    )

    response = client.models.generate_content(model = model, contents = contents, config = generate_content_config)
    response = response.candidates[0].content.parts[0].text
    response = clean_json_from_gemini(response)
    
    return response

def agent_main(gemini_api_key):
    patient = get_patient_info()
    criteria_list, nct_ids = return_trial_info(
        patient["age"], patient["diagnosis"], patient["gender"], patient["country"]
    )

    results = []
    for criteria, trial_id in zip(criteria_list, nct_ids):
        try:
            result = evaluate_eligibility_with_llm(patient, criteria, trial_id, gemini_api_key)
            results.append(result)
        except Exception as e:
            results.append({
                "trial_id": trial_id,
                "match_criteria": "unknown",
                "reason": f"LLM error: {e}"
            })

    return results

result = agent_main(os.getenv("GEMINI_API_KEY"))