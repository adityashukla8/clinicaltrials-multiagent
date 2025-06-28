import json
import re
import os
from collections import Counter
from google import genai
from google.genai import types
import logging

from tools.appwrite_get_all_patients import fetch_all_patients
from tools.single_trial_search import fetch_trial_details_by_nct_id

from ipdb import set_trace as ipdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def clean_json_from_gemini(raw_text):
    """Extract valid JSON from Gemini LLM output."""
    return json.loads(re.sub(r"^```json\s*|\s*```$", "", raw_text.strip(), flags=re.DOTALL))

def biomarker_optimization_agent(state):
    """
    Agent that suggests optimized biomarker thresholds for clinical trials 
    based on patient population.
    """
    patients = state["patients_info_list"]
    trial = state["trial_info"]

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Missing GEMINI_API_KEY")

    # Initialize Gemini
    client = genai.Client(vertexai=False, project="ai-in-action-461412", location="global")
    model = "gemini-2.5-flash"

    # Build biomarker distribution
    biomarkers = [p["biomarker"] for p in patients if "biomarker" in p and p["biomarker"]]
    biomarker_distribution = dict(Counter(biomarkers))

    logger.info(f"Biomarker distribution across {len(patients)} patients: {biomarker_distribution}")

    prompt = types.Part.from_text(text=f"""
You are a clinical trial protocol optimization expert.

You are analyzing a trial with the following biomarker eligibility criteria:
"{trial.get('eligibility_criteria', 'N/A')}"

Here is the distribution of biomarkers in real patients:
{json.dumps(biomarker_distribution, indent=2)}

Suggest whether the biomarker criteria should be broadened or adjusted to include more patients, without sacrificing scientific integrity.

Respond in the following JSON format:
{{
  "summary": "Brief recommendation summary",
  "suggested_biomarker_criteria": "Suggested revised biomarker inclusion logic",
  "gain_estimate": "Approximate % increase in eligible patients if revised",
  "clinical_note": "Optional clinical rationale or warnings"
}}
""")

    try:
        response = client.models.generate_content(
            model=model,
            contents=[types.Content(role="user", parts=[prompt])],
            config=types.GenerateContentConfig(
                temperature=0.3,
                top_p=1,
                max_output_tokens=2048,
                safety_settings=[],
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        # ipdb()
        raw = response.candidates[0].content.parts[0].text
        result = clean_json_from_gemini(raw)
        logger.info("Biomarker Threshold Agent response parsed successfully.")
        state["biomarker_optimization_result"] = result
        return state

    except Exception as e:
        logger.error(f"Error from Biomarker Agent: {e}")
        state["biomarker_optimization_result"] = {
            "summary": "Error occurred",
            "error": str(e)
        }
        return state

# if __name__ == "__main__":
#     trial_info = fetch_trial_details_by_nct_id("NCT06750094")
#     patient_info_list = fetch_all_patients()
#     state = {
#         "trial": trial_info,
#         "patients": patient_info_list
#     }
#     optimized_state = analyze_biomarker_threshold(state)