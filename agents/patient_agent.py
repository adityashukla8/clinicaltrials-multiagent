import logging
from appwrite.query import Query
from tools.appwrite_client import init_appwrite, DATABASE_ID, COLLECTION_ID

from ipdb import set_trace as ipdb

logger = logging.getLogger(__name__)

def get_patient_info_tool(state):
    patient_id = state.get("patient_id")
    logger.info(f"Fetching patient info for patient_id: {patient_id}")
    databases = init_appwrite()

    try:
        response = databases.list_documents(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            queries=[Query.equal("patient_id", patient_id)]
        )
        logger.info(f"Received response from database for patient_id: {patient_id}")
    except Exception as e:
        logger.error(f"Error fetching patient info for patient_id {patient_id}: {e}")
        raise

    if not response['documents']:
        logger.warning(f"No patient document found for patient_id: {patient_id}")
        state["patient_info"] = {}
        return state

    doc = response['documents'][0]
    logger.debug(f"Patient document: {doc}")

    state["patient_info"] = {
        "age": doc["age"],
        "diagnosis": doc["condition"],
        "treatment_history": [doc["chemotherapy"]],
        "country": doc["country"],
        "gender": doc["gender"],
        "ecog_score": doc["ecog_score"],
        "biomarker": doc["biomarker"],
        "metastasis": doc["metastasis"],
        "radiotherapy": doc["radiotherapy"],
        "histology": doc["histology"],
        "condition_recurrence": doc["condition_recurrence"]
    }
    # ipdb()
    logger.info(f"Patient info added to state for patient_id: {patient_id}")
    
    return state
