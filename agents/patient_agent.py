from appwrite.query import Query
from tools.appwrite_client import init_appwrite, DATABASE_ID, COLLECTION_ID

def get_patient_info_tool(state):
    patient_id = state.get("patient_id")
    databases = init_appwrite()

    response = databases.list_documents(
        database_id=DATABASE_ID,
        collection_id=COLLECTION_ID,
        queries=[Query.equal("patient_id", patient_id)]
    )

    doc = response['documents'][0]
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
    return state
