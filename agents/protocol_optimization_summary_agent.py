import os
import json
import logging
from google import genai
from google.genai import types

from tools.appwrite_write_trial_info import write_protocol_optimization

from ipdb import set_trace as ipdb

logger = logging.getLogger(__name__)

def format_supervisor_prompt(age_optimization_result, biomarker_optimization_result, trial_info):
    return types.Part.from_text(text=f"""
You are a clinical trial optimization assistant. Summarize and contextualize the protocol optimization recommendations based on the outputs of two analysis agents:

TRIAL INFO:
- Title: {trial_info.get("title", "N/A")}
- Current Age Range: {trial_info.get("minimum_age", "N/A")} to {trial_info.get("maximum_age", "N/A")}
- Biomarker Eligibility: {trial_info.get("eligibility_criteria", "N/A")[:500]}...

AGE GAP ANALYSIS RESULT:
{json.dumps(age_optimization_result, indent=2)}

BIOMARKER ANALYSIS RESULT:
{json.dumps(biomarker_optimization_result, indent=2)}

Your job:
- Compare the agent suggestions with the original trial criteria.
- Generate a crisp, clinical summary of what was optimized and why.
- Use percentages if estimates are present.
- Keep language clear and informative for medical reviewers.

Respond strictly in the following JSON format:
{{
  "summary": "A crisp, bulleted clinical summary of the optimization decisions and expected impact. Should be withing 1073741824 characters",
  "age_optimization_result": {json.dumps(age_optimization_result)},
  "biomarker_optimization_result": {json.dumps(biomarker_optimization_result)}
}}
""")

def protocol_optimization_summary(state):
    gemini = genai.Client(vertexai=True, project="ai-in-action-461412", location="global")
    model = "gemini-2.5-flash"

    age_optimization_result = state.get("age_optimization_result", {})
    biomarker_optimization_result = state.get("biomarker_optimization_result", {})
    trial_info = state.get("trial_info", {})

    prompt_text = format_supervisor_prompt(age_optimization_result, biomarker_optimization_result, trial_info)

    try:
        contents = [types.Content(role="user", parts=[prompt_text])]
        config = types.GenerateContentConfig(
            temperature=0.3,
            top_p=1,
            safety_settings=[],
        )
        response = gemini.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )

        # ipdb()

        raw = response.candidates[0].content.parts[0].text
        output = json.loads(raw.strip().removeprefix("```json").removesuffix("```"))
        logger.info("Supervisor summary generated successfully.")

        write_protocol_optimization(state['trial_id'], output)

        state["supervisor_summary"] = output

        return state

    except Exception as e:
        logger.error(f"LLM Supervisor Agent failed: {e}")
        return {
            "summary": f"Error generating summary: {e}",
            "age_optimization_result": age_optimization_result,
            "biomarker_optimization_result": biomarker_optimization_result
        }
    

# if __name__ == "__main__":
#     trial_info = fetch_trial_details_by_nct_id("NCT06750094")
#     patients_list = fetch_all_patients()

#     state = {
#         "trial_id": "NCT06750094",
#         "trial_info": trial_info,
#         "patients_info_list": patients_list
#     }

#     age_optimization_result = age_gap_analysis_agent(state)
#     biomarker_optimization_result = analyze_biomarker_threshold(state)

#     supervisor_summary = format_final_output(state)