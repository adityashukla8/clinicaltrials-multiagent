import json
import os
import re
from google import genai
from google.genai import types

from ipdb import set_trace as ipdb

def clean_json_from_gemini(raw_text):
    return json.loads(re.sub(r"^```json\s*|\s*```$", "", raw_text.strip(), flags=re.DOTALL))

def evaluate_trials_llm(state):
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
            safety_settings=[],
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
