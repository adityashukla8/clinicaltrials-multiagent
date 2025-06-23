from appwrite.query import Query
from appwrite_client import init_appwrite, DATABASE_ID, TRIAL_INFO_COLLECTION_ID
import logging
from ipdb import set_trace as ipdb

logger = logging.getLogger(__name__)

def insert_or_update_trial_to_appwrite(trial: dict):
    db = init_appwrite()

    # Step 1: Search for existing trial with same trial_id
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
