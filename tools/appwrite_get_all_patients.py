from appwrite.query import Query
from tools.appwrite_client import init_appwrite, DATABASE_ID, COLLECTION_ID
import logging
from ipdb import set_trace as ipdb

def fetch_all_patients():
    db = init_appwrite()
    patients = []
    limit = 200
    offset = 0

    while True:
        response = db.list_documents(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            queries=[
                Query.limit(limit),
                Query.offset(offset)
            ]
        )

        logging.info(f"Fetched {response['total']} documents from Appwrite.")

        documents = response['documents']
        if not documents:
            break

        for doc in documents:
            patients.append({
                "patient_id": doc.get("patient_id"),
                "age": doc.get("age"),
                "diagnosis": doc.get("condition"),
                "treatment_history": {'chemothrepy': doc.get("chemotherapy"), 'radiotherapy': doc.get("radiotherapy")},
                "country": doc.get("country"),
                "gender": doc.get("gender"),
                "ecog_score": doc.get("ecog_score"),
                "biomarker": doc.get("biomarker"),
                "metastasis": doc.get("metastasis"),
                "histology": doc.get("histology"),
                "condition_recurrence": doc.get("condition_recurrence"),
                "radiotherapy": doc.get("radiotherapy")
            })

        offset += limit

    # ipdb()
    return patients

def fetch_patient_by_id(patient_id: str):
    db = init_appwrite()
    try:
        response = db.list_documents(
            database_id=DATABASE_ID,
            collection_id=COLLECTION_ID,
            queries=[Query.equal("patient_id", patient_id)]
        )
        if not response['documents']:
            return None
        return response['documents'][0]
    except Exception as e:
        logging.error(f"Error fetching patient: {e}")
        return None

# if __name__ == "__main__":
#     patients = fetch_all_patients()