from fastapi import FastAPI
from fastapi import HTTPException

from tools.appwrite_get_all_patients import fetch_all_patients, fetch_patient_by_id
from clinical_trials_match import match_trials

from pydantic import BaseModel

app = FastAPI()

class MatchRequest(BaseModel):
    patient_id: str

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/patients")
def get_patients():
    patients = fetch_all_patients()
    return patients

@app.get("/patients/{patient_id}")
def get_patient_by_id(patient_id: str):
    patient = fetch_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.post("/matchtrials")
def run_trial_match(payload: MatchRequest):
    try:
        matched_trials = match_trials(payload.patient_id)
        return {"success": True, "matches": matched_trials}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/matchtrials/{patient_id}")
# def run_trial_match_get(patient_id: str):
#     try:
#         matched_trials = match_trials(patient_id)
#         return {"success": True, "matches": matched_trials}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
