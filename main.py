from fastapi import FastAPI
from fastapi import HTTPException

from tools.appwrite_get_all_patients import fetch_all_patients, fetch_patient_by_id

app = FastAPI()

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/patients")
def get_patients():
    patients = fetch_all_patients()
    return {"patients": patients}

@app.get("/patients/{patient_id}")
def get_patient_by_id(patient_id: str):
    patient = fetch_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
