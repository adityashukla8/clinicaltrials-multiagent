from appwrite.query import Query
from collections import defaultdict
from tools.appwrite_client import init_appwrite, DATABASE_ID, COLLECTION_ID, TRIAL_INFO_COLLECTION_ID, TRIAL_SUMMARY_COLLECTION_ID, MATCH_COLLECTION_ID

db = init_appwrite()

from ipdb import set_trace as ipdb

# Collection IDs
PATIENTS = COLLECTION_ID
TRIAL_INFO = TRIAL_INFO_COLLECTION_ID
MATCH_INFO = MATCH_COLLECTION_ID
SUMMARY_COLLECTION = TRIAL_SUMMARY_COLLECTION_ID


def fetch_all_documents(collection_id):
    documents = []
    last_id = None

    while True:
        queries = [Query.limit(100)]
        if last_id:
            queries.append(Query.cursor_after(last_id))

        res = db.list_documents(DATABASE_ID, collection_id, queries=queries)
        docs = res["documents"]
        if not docs:
            break
        documents.extend(docs)
        last_id = docs[-1]["$id"]

    return documents

# Fetch all enriched trials from summary_info collection
def fetch_summary_trials():
    enriched = []
    offset = 0
    limit = 100
    while True:
        result = db.list_documents(DATABASE_ID, SUMMARY_COLLECTION, queries=[
            Query.limit(limit),
            Query.offset(offset)
        ])
        enriched.extend(result["documents"])
        if len(result["documents"]) < limit:
            break
        offset += limit
    return enriched

def get_appwrite_metrics():
    patients = fetch_all_documents(PATIENTS)
    trials = fetch_all_documents(TRIAL_INFO)
    matches = fetch_all_documents(MATCH_INFO)

    total_patients = len(patients)
    total_trials = len(trials)

    # Get unique patient IDs from match records
    patient_ids_in_matches = set(match["patient_id"] for match in matches)
    total_patients_scanned = len(patient_ids_in_matches)

    # Trials per patient
    trial_counts_per_patient = defaultdict(set)
    for match in matches:
        trial_counts_per_patient[match["patient_id"]].add(match["trial_id"])

    avg_trials_scanned = round(
        sum(len(trials) for trials in trial_counts_per_patient.values()) / total_patients_scanned, 2
    ) if total_patients_scanned else 0

    matched_patients = set(
        match["patient_id"]
        for match in matches
        if match.get("match_criteria", "").lower() == "match"
    )
    total_patients_with_match = len(matched_patients)

    matched_trial_ids = set(
        match["trial_id"]
        for match in matches
        if match.get("match_criteria", "").lower() == "match"
    )
    total_matched_trials = len(matched_trial_ids)

    match_rate = round((total_patients_with_match / total_patients_scanned) * 100, 2) if total_patients_scanned else 0

    condition_counter = defaultdict(int)
    for patient in patients:
        if patient["patient_id"] in matched_patients:
            condition_counter[patient["condition"]] += 1

    top_conditions = sorted(condition_counter.items(), key=lambda x: x[1], reverse=True)[:5]

    enriched_trials = fetch_summary_trials()
    num_enriched_trials = len(enriched_trials)

    # Average Tavily citations per trial
    citations_per_trial = [
        len(t.get("citations", [])) if isinstance(t.get("citations"), list) else 0
        for t in enriched_trials
    ]
    avg_citations = round(sum(citations_per_trial) / num_enriched_trials, 2) if num_enriched_trials else 0

    metrics = {
        "total_patients": total_patients,
        "total_trials": total_trials,
        "total_patients_scanned": total_patients_scanned,
        "patients_with_match": total_patients_with_match,
        "total_matched_trials": total_matched_trials,
        "avg_trials_scanned_per_patient": avg_trials_scanned,
        "match_rate_percent": match_rate,
        "top_matched_conditions": top_conditions,
        "trials_enriched": num_enriched_trials,
        "avg_tavily_citations_per_trial": avg_citations,
    }

    return metrics
# ipdb()