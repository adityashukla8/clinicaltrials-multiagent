from appwrite.client import Client
from appwrite.services.databases import Databases
import os

def init_appwrite():
    client = Client()
    client.set_endpoint(os.getenv("APPWRITE_API_ENDPOINT"))
    client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
    client.set_key(os.getenv("APPWRITE_API_KEY"))
    return Databases(client)

DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID")
COLLECTION_ID = os.getenv("APPWRITE_COLLECTION_ID")
