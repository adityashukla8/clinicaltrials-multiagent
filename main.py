from fastapi import FastAPI
from fastapi import HTTPException, status

from tools.appwrite_get_all_patients import fetch_all_patients, fetch_patient_by_id
from tools.clinical_trials_match import match_trials
from tools.appwrite_write_trial_info import fetch_trial_info

from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class MatchRequest(BaseModel):
    patient_id: str

class TrialInfoRequest(BaseModel):
    patient_id: str

class TrialInfo(BaseModel):
    trial_id: str
    match_criteria: Optional[str]
    reason: Optional[str]
    match_requirements: Optional[str]
    title: Optional[str]
    phase: Optional[str]
    condition: Optional[str]
    status: Optional[str]
    location: Optional[str]
    eligibility: Optional[str]
    source_url: Optional[str]

class TrialInfoResponse(BaseModel):
    success: bool
    trials: List[TrialInfo]

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

@app.post("/trial_info", response_model=TrialInfoResponse)
def get_trial_info(payload: TrialInfoRequest):
    try:
        trials = fetch_trial_info(payload.patient_id)
        return {
            "success": True,
            "trials": trials
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/matchtrials")
def run_trial_match(payload: MatchRequest):
    try:
        matched_trials = match_trials(payload.patient_id)
        return {"success": True, "matches": matched_trials}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
