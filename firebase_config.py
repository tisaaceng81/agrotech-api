import os
import firebase_admin
from firebase_admin import credentials, db as realtime_db
from dotenv import load_dotenv

load_dotenv()

private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")

cred_dict = {
    "type": "service_account",
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key": private_key,
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "token_uri": "https://oauth2.googleapis.com/token",
}

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    # Inicializa com a URL do Realtime Database
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
    })

rtdb = realtime_db
