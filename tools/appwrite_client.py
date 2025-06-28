from appwrite.client import Client
from appwrite.services.databases import Databases
import os

from ipdb import set_trace as ipdb

def init_appwrite():
    client = Client()
    client.set_endpoint(os.getenv("APPWRITE_API_ENDPOINT"))
    client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
    client.set_key(os.getenv("APPWRITE_API_KEY"))
    return Databases(client)

DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")
COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_ID")
TRIAL_INFO_COLLECTION_ID = os.getenv("APPWRITE_TRIALS_INFO_COLLECTION_ID")
TRIAL_SUMMARY_COLLECTION_ID = os.getenv("APPWRITE_TRIAL_SUMMARY_COLLECTION_ID")
MATCH_COLLECTION_ID = os.getenv("APPWRITE_MATCH_COLLECTION_ID")
PROTOCOL_OPTIMIZATION_COLLECTION_ID = os.getenv("APPWRITE_PROTOCOL_OPTIMIZATION_COLLECTION_ID")