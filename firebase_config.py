import os
import json
import firebase_admin
from firebase_admin import credentials, db as realtime_db
from dotenv import load_dotenv

load_dotenv()

cred_dict = None
firebase_credentials_raw = os.getenv("FIREBASE_CREDENTIALS")

# 1. Tenta carregar o JSON completo se a variável existir
if firebase_credentials_raw:
    try:
        raw_str = firebase_credentials_raw.strip().strip('"').strip("'")
        cred_dict = json.loads(raw_str)
    except Exception as e:
        print(f"Erro ao ler FIREBASE_CREDENTIALS: {e}")
        cred_dict = None

# 2. Se não encontrou o JSON completo, tenta montar pelas variáveis avulsas
if not cred_dict:
    cred_dict = {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", ""),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }

# 3. TRATAMENTO CRÍTICO DA CHAVE PRIVADA (Corrige MalformedFraming do telemóvel)
if cred_dict and "private_key" in cred_dict and cred_dict["private_key"]:
    pk = str(cred_dict["private_key"])
    
    # Remove aspas externas indesejadas
    pk = pk.strip().strip('"').strip("'")
    
    # Converte '\\n' literal em quebra de linha real '\n'
    pk = pk.replace("\\n", "\n")
    
    # Garante cabeçalho e rodapé limpos
    cred_dict["private_key"] = pk

if not firebase_admin._apps:
    database_url = os.getenv("FIREBASE_DATABASE_URL")
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': database_url
    })

rtdb = realtime_db
