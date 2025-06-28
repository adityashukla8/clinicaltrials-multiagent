import os
import json
import re
import logging

from typing import List, Dict
from google import genai
from google.genai import types

from tools.appwrite_get_all_patients import fetch_all_patients
from tools.single_trial_search import fetch_trial_details_by_nct_id

from ipdb import set_trace as ipdb

logger = logging.getLogger(__name__)

patients_list = fetch_all_patients()
logger.info(f"Fetched {len(patients_list)} patients from Appwrite.")

def clean_json_from_gemini(raw_text):
    return json.loads(re.sub(r"^```json\s*|\s*```$", "", raw_text.strip(), flags=re.DOTALL))

from concurrent.futures import ThreadPoolExecutor, as_completed

def evaluate_trial_against_patients(trial, patient_list, max_workers=10):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(vertexai=True, project="ai-in-action-461412", location="global")
    model = "gemini-2.5-flash"
    
    logger.info(f"Evaluating trial {trial['trial_id']} against {len(patient_list)} patients.")
    results = []

    def evaluate_single_patient(patient):
        prompt = types.Part.from_text(text=f"""You are a clinical trials assistant. Determine if the following patient qualifies for the trial criteria.

PATIENT:
{json.dumps(patient, indent=2)}

TRIAL ID: {trial['trial_id']}
CRITERIA:
\"\"\"
{trial['eligibility_criteria']}
\"\"\"

If more info is needed, assume the patient meets requirements, you can be a little flexible.
Reply strictly in this JSON format:
{{
  "patient_id": "{patient['patient_id']}",
  "match_criteria": "match" or "not match",
  "reason": "brief explanation",
  "match_requirements": "if no match, specify what changes in patient profile could lead to a match"
}}
""")

        contents = [types.Content(role="user", parts=[prompt])]
        config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=1,
            seed=0,
            max_output_tokens=4096,
            safety_settings=[],
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        try:
            response = client.models.generate_content(model=model, contents=contents, config=config)
            raw = response.candidates[0].content.parts[0].text
            parsed = clean_json_from_gemini(raw)
            logger.info(f"LLM evaluation complete for patient_id: {patient['patient_id']}")
            return parsed
        except Exception as e:
            logger.error(f"Error processing patient_id: {patient['patient_id']} — {e}")
            return {
                "patient_id": patient["patient_id"],
                "match_criteria": "unknown",
                "reason": f"LLM error: {e}"
            }

    # Use ThreadPoolExecutor to evaluate in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_patient = {executor.submit(evaluate_single_patient, patient): patient for patient in patient_list}

        for future in as_completed(future_to_patient):
            results.append(future.result())

    logger.info(f"Completed evaluation for all patients against trial_id: {trial['trial_id']}")
    return {
        "trial_id": trial["trial_id"],
        "total_patients": len(patient_list),
        "match_count": sum(1 for r in results if r["match_criteria"] == "match"),
        "results": results
    }

# if __name__ == "__main__":
    
#     patients_list = fetch_all_patients()
#     ipdb()

#     nct_id = "NCT06614192"
#     trial = fetch_trial_details_by_nct_id(nct_id)

#     if trial:
#         results = evaluate_trial_against_patients(trial, patients_list)
        