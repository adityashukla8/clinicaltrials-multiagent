from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from typing import TypedDict, List, Annotated
import os
import json
import logging
import requests
import re

from google import genai
from google.genai import types

# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class TrialMatch(TypedDict):
    trial_id: str
    match_criteria: str
    reason: str

class AgentState(TypedDict):
    patient_info: dict
    trials: List[dict]
    results: List[TrialMatch]

def get_patient_info_tool(state: AgentState) -> AgentState:
    state["patient_info"] = {
        "age": 52,
        "diagnosis": "Cancer of the Uterine Cervix",
        "treatment_history": ["taxane-based chemotherapy"],
        "country": "USA",
        "gender": "Female"
    }
    return state

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
            nextPageToken = data.get('nextPageToken')
            if nextPageToken and studies_fetched < max_studies:
                params['pageToken'] = nextPageToken
            else:
                break
        else:
            logger.error(f"Failed to fetch data. Status code: {response.status_code}")
            break

    return eligibility_criteria, nct_ids

def return_trial_info_tool(state: AgentState) -> AgentState:
    patient = state["patient_info"]
    critlist, nctidlist = fetch_clinical_trial_data(patient["diagnosis"], 10)
    trials = [{"trial_id": tid, "criteria": crit} for tid, crit in zip(nctidlist, critlist)]
    state["trials"] = trials
    return state

def clean_json_from_gemini(raw_text):
    cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
    return json.loads(cleaned)

def evaluate_trials_llm(state: AgentState) -> AgentState:
    patient_info = state["patient_info"]
    trials = state["trials"]
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(vertexai=True, project="ai-in-action-461412", location="global")

    model = "gemini-2.5-flash"
    results = []
    for trial in trials:
        prompt = types.Part.from_text(text=f"""You are a clinical trials assistant. Determine if the following patient qualifies for the trial criteria.

PATIENT:
{json.dumps(patient_info, indent=2)}

TRIAL ID: {trial['trial_id']}
CRITERIA:
\"\"\"
{trial['criteria']}
\"\"\"

Reply strictly in this JSON format:
{{
  "trial_id": "{trial['trial_id']}",
  "match_criteria": "match" or "not match",
  "reason": "brief explanation"
}}
        """)

        contents = [types.Content(role="user", parts=[prompt])]

        generate_content_config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=1,
            seed=0,
            max_output_tokens=4096,
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
            ],
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        try:
            response = client.models.generate_content(model=model, contents=contents, config=generate_content_config)
            raw = response.candidates[0].content.parts[0].text
            parsed = clean_json_from_gemini(raw)
            results.append(parsed)
        except Exception as e:
            results.append({
                "trial_id": trial["trial_id"],
                "match_criteria": "unknown",
                "reason": f"LLM error: {e}"
            })

    state["results"] = results
    return state

def create_workflow(agent_state):
    workflow = StateGraph(AgentState)
    workflow.add_node("get_patient_info", get_patient_info_tool)
    workflow.add_node("fetch_trials", return_trial_info_tool)
    workflow.add_node("llm_evaluation", evaluate_trials_llm)

    workflow.set_entry_point("get_patient_info")
    workflow.add_edge("get_patient_info", "fetch_trials")
    workflow.add_edge("fetch_trials", "llm_evaluation")
    workflow.add_edge("llm_evaluation", END)
    
    app = workflow.compile()

    return app

def main():
    app = create_workflow(AgentState())

    final_state = app.invoke({})

    return final_state['results']

if __name__ == "__main__":
    results = main()
    print(json.dumps(results, indent=2))
    logger.info("Trial matching completed successfully.")