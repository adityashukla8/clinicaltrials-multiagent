from google import genai
from google.genai import types
import os
import json

from tools.single_trial_search import fetch_trial_details_by_nct_id
from tools.appwrite_get_all_patients import fetch_all_patients

from ipdb import set_trace as ipdb

# trial_info = fetch_trial_details_by_nct_id("NCT06750094")
# patients_info_list = fetch_all_patients()
# ipdb()

def age_optimization_agent(state):
    trial = state['trial_info']
    patients = state['patients_info_list']

    def parse_age(age_str):
        try:
            return int(age_str.split()[0]) if age_str != "N/A" else None
        except:
            return None

    trial_min_age = parse_age(trial.get("minimum_age", "N/A"))
    trial_max_age = parse_age(trial.get("maximum_age", "N/A"))

    eligible = 0
    missed = 0
    missed_upper_range = []
    missed_lower_range = []

    for p in patients:
        age = p.get("age")
        if age is None:
            continue
        if trial_min_age and age < trial_min_age:
            missed += 1
            missed_lower_range.append(age)
        elif trial_max_age and age > trial_max_age:
            missed += 1
            missed_upper_range.append(age)
        else:
            eligible += 1

    upper_suggest = max(missed_upper_range) if missed_upper_range else None
    lower_suggest = min(missed_lower_range) if missed_lower_range else None

    metrics = {
        "eligible_patients": eligible,
        "missed_patients": missed,
        "missed_due_to_upper_limit": len(missed_upper_range),
        "missed_due_to_lower_limit": len(missed_lower_range),
        "suggested_upper_bound": upper_suggest,
        "suggested_lower_bound": lower_suggest,
        "current_range": f"{trial_min_age}–{trial_max_age}",
        "suggested_range": f"{lower_suggest or trial_min_age}–{upper_suggest or trial_max_age}",
        "total_patients": len(patients)
    }

    # Send to LLM for clinical summary
    gemini = genai.Client(vertexai=True, project="ai-in-action-461412", location="global")
    model = "gemini-2.5-flash"

    prompt = types.Part.from_text(text=f"""
You are a clinical trial design analyst. Based on the patient eligibility data below, generate a structured, human-readable optimization report.

Data:
{json.dumps(metrics, indent=2)}

Respond in the following JSON format:
{{
  "summary": "Brief one-line impact statement",
  "clinical_recommendation": "Suggested action",
  "revised_age_range": "Suggested new range",
  "eligibility_gain_estimate": "Approx % improvement",
  "note": "Optional clinical comment"
}}
""")
    # ipdb()
    contents = [types.Content(role="user", parts=[prompt])]
    response = gemini.models.generate_content(model=model, contents= contents)
    llm_summary = response.candidates[0].content.parts[0].text

    try:
        structured_output = json.loads(llm_summary.strip("```json\n").strip("```"))
    except Exception as e:
        structured_output = {
            "summary": "LLM failed to generate output",
            "clinical_recommendation": "",
            "revised_age_range": "",
            "eligibility_gain_estimate": "",
            "note": f"Error: {e}"
        }

    state["age_optimization_result"] = {
        "quantitative": metrics,
        "llm_insight": structured_output
    }

    return state

# if __name__ == "__main__":
#     state = age_gap_analysis_agent(trial_info, patient_info_list)