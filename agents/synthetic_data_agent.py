from google import genai
from tools.appwrite_client import init_appwrite, DATABASE_ID, COLLECTION_ID

import json
from ipdb import set_trace as ipdb

db_schema = {
    "patient_id": str,
    "patient_name": str,
    "condition": str,
    "chemotherapy": str,
    "radiotherapy": str,
    "age": int,
    "gender": str,
    "country": str,
    "metastasis": str,
    "histology": str,
    "biomarker": str,
    "ecog_score": int,
    "condition_recurrence": str
}

def generate_patient_info(synthetic_data_count, db_schema=db_schema):
    client = genai.Client(vertexai=True, project="ai-in-action-461412", location="global")

    prompt = f"""
You are a clinical data simulator.
Generate {synthetic_data_count} synthetic but realistic cancer patient profiles, based on this schema:
{json.dumps(list(db_schema.keys()))}

Conditions:
- Return a list of JSON objects (no markdown formatting).
- Each patient must contain: {", ".join(db_schema.keys())}.
- 70% of patients should be from USA.
- No nulls, empty strings, or missing fields.
- Where boolean fields are required, use "Yes" or "No".

Respond in raw JSON list format only.
"""

    contents = [genai.types.Content(role="user", parts=[genai.types.Part.from_text(text=prompt)])]
    config = genai.types.GenerateContentConfig(temperature=0.3)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=contents, config=config)

    raw = response.candidates[0].content.parts[0].text.strip()
    cleaned = raw.strip("```json").strip("```").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("❌ LLM output was not valid JSON")
        raise e

def write_patient_info_to_appwrite(patient_data):
    databases = init_appwrite()
    response = databases.create_document(
        database_id=DATABASE_ID,
        collection_id=COLLECTION_ID,
        document_id="unique()",
        data=patient_data
    )
    return response

def main(synthetic_data_count, write_to_appwrite):
    patient_data = generate_patient_info(synthetic_data_count)
    
    if write_to_appwrite:
        for record in patient_data:
            try:
                write_patient_info_to_appwrite(record)
            except Exception as e:
                print(f"Error writing patient data to Appwrite: {e}")
            print(f"Patient data written to Appwrite: {record['patient_id']}")

    # print(json.dumps(patient_data, indent=2))

if __name__ == "__main__":
    write_to_appwrite=True
    synthetic_data_count=200
    main(synthetic_data_count, write_to_appwrite=write_to_appwrite)
