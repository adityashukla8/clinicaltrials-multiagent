from appwrite.query import Query
from appwrite_client import init_appwrite, DATABASE_ID, TRIAL_INFO_COLLECTION_ID, TRIAL_SUMMARY_COLLECTION_ID, MATCH_COLLECTION_ID
import logging
from datetime import datetime

from ipdb import set_trace as ipdb

logger = logging.getLogger(__name__)

db = init_appwrite()

def insert_or_update_trial_to_appwrite(trial: dict):
    existing = db.list_documents(
        database_id=DATABASE_ID,
        collection_id=TRIAL_INFO_COLLECTION_ID,
        queries=[Query.equal("trial_id", trial["trial_id"])]
    )

    if existing["total"] > 0:
        document_id = existing["documents"][0]["$id"]
        logger.info(f"Trial {trial['trial_id']} exists, updating...")
        return db.update_document(
            database_id=DATABASE_ID,
            collection_id=TRIAL_INFO_COLLECTION_ID,
            document_id=document_id,
            data=trial
        )
    else:
        logger.info(f"Trial {trial['trial_id']} not found, creating...")
        return db.create_document(
            database_id=DATABASE_ID,
            collection_id=TRIAL_INFO_COLLECTION_ID,
            document_id=trial["trial_id"],
            data=trial
        )

def flatten_summary_card(summary_card):
    flat = {
        "trial_id": summary_card["nct_id"],
        "created_at": datetime.utcnow().isoformat(),
        "citations": [],
    }

    for key, section in summary_card["sections"].items():
        flat[key] = section.get("summary", "")
        flat["citations"].extend(section.get("citations", []))

    return flat

def insert_trial_summary_to_appwrite(summary_card):
    flat_data = flatten_summary_card(summary_card)
    trial_id = flat_data["trial_id"]

    existing = db.list_documents(
        database_id=DATABASE_ID,
        collection_id=TRIAL_SUMMARY_COLLECTION_ID,
        queries=[Query.equal("trial_id", trial_id)]
    )

    if existing["total"] > 0:
        logger.info(f"Summary for {trial_id} exists, updating...")
        doc_id = existing["documents"][0]["$id"]
        return db.update_document(
            database_id=DATABASE_ID,
            collection_id=TRIAL_SUMMARY_COLLECTION_ID,
            document_id=doc_id,
            data=flat_data
        )
    else:
        logger.info(f"Summary for {trial_id} not found, creating...")
        return db.create_document(
            database_id=DATABASE_ID,
            collection_id=TRIAL_SUMMARY_COLLECTION_ID,
            document_id=trial_id,
            data=flat_data
        )
    
def insert_match_to_appwrite(match: dict, patient_id):
    match_id = f"{patient_id}_{match['trial_id']}"
    
    data = {
        "match_id": match_id,
        "patient_id": patient_id,
        "trial_id": match["trial_id"],
        "match_criteria": match["match_criteria"],
        "reason": match.get("reason", ""),
        "match_requirements": match.get("match_requirements", "")
    }

    existing = db.list_documents(
        database_id=DATABASE_ID,
        collection_id=MATCH_COLLECTION_ID,
        queries=[Query.equal("match_id", match_id)]
    )

    if existing["total"] > 0:
        doc_id = existing["documents"][0]["$id"]
        return db.update_document(
            database_id=DATABASE_ID,
            collection_id=MATCH_COLLECTION_ID,
            document_id=doc_id,
            data=data
        )
    else:
        return db.create_document(
            database_id=DATABASE_ID,
            collection_id=MATCH_COLLECTION_ID,
            document_id=match_id,
            data=data
        )
