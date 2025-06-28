from fastapi import FastAPI
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from tools.appwrite_get_all_patients import fetch_all_patients, fetch_patient_by_id
from tools.clinical_trials_match import match_trials
from tools.run_protocol_optimization_workflow import run_protocol_optimization
from tools.appwrite_write_trial_info import fetch_trial_info, fetch_all_trials, get_protocol_optimization_by_trial_id, get_all_protocol_optimizations
from tools.appwrite_metrics import get_appwrite_metrics

from pydantic import BaseModel
from typing import List, Optional, Any, Dict

from ipdb import set_trace as ipdb

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

class TrialData(BaseModel):
    trial_id: str
    title: Optional[str]
    source_url: Optional[str]
    eligibility: Optional[str]
    official_title: Optional[str]
    known_side_effects: Optional[str]
    dsmc_presence: Optional[str]
    enrollment_info: Optional[str]
    objective_summary: Optional[str]
    external_notes: Optional[str]
    sponsor_info: Optional[str]
    patient_experiences: Optional[str]
    statistical_plan: Optional[str]
    intervention_arms: Optional[str]
    sample_size: Optional[str]
    pre_req_for_participation: Optional[str]
    sponsor_contact: Optional[str]
    location_and_site_details: Optional[str]
    monitoring_frequency: Optional[str]
    safety_documents: Optional[str]
    sites: Optional[str]
    patient_faq_summary: Optional[str]
    citations: Optional[List[str]] = []
    matched_patients_count: int

class TrialListResponse(BaseModel):
    success: bool
    trials: List[TrialData]

class TrialIDRequest(BaseModel):
    trial_id: str

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
    

@app.get("/all_trials", response_model=TrialListResponse)
def get_all_trials():
    try:
        trials = fetch_all_trials()
        return {
            "success": True,
            "trials": trials
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
def get_metrics():
    try:
        metrics = get_appwrite_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return JSONResponse(content=metrics)

@app.get("/search-protocols/{trial_id}")
def read_optimization_by_trial_id(trial_id: str):
    result = get_protocol_optimization_by_trial_id(trial_id)
    if not result:
        raise HTTPException(status_code=404, detail="Trial not found")
    return result

@app.get("/search-protocols")
def read_all_optimizations():
    result = get_all_protocol_optimizations()
    return JSONResponse(content=result)

class OptimizationRequest(BaseModel):
    trial_id: str

class OptimizationResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = {}
    error: str = None

@app.post("/optimize-protocol", response_model=OptimizationResponse)
def optimize_protocol(request: OptimizationRequest):
    try:
        result = run_protocol_optimization(request.trial_id)
        return {
            "success": True,
            "data": result,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }
