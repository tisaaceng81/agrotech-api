import os
import json
import firebase_admin
from firebase_admin import credentials, db as realtime_db
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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

# 3. TRATAMENTO CRÍTICO DA CHAVE PRIVADA
if cred_dict and "private_key" in cred_dict and cred_dict["private_key"]:
    pk = str(cred_dict["private_key"])
    pk = pk.strip().strip('"').strip("'")
    pk = pk.replace("\\n", "\n")
    cred_dict["private_key"] = pk

if not firebase_admin._apps:
    database_url = os.getenv("FIREBASE_DATABASE_URL")
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': database_url
    })

rtdb = realtime_db

app = FastAPI(
    title="API AgroTech Completa",
    description="Backend FastAPI com Gestão Completa via App",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ManejoSchema(BaseModel):
    cultura: str
    area: str
    tipo: str
    quantidade: str
    observacao: Optional[str] = ""
    uid_usuario: str

class UsuarioSchema(BaseModel):
    uid: str
    nome: str
    email: str
    role: Optional[str] = "user"

@app.get("/health")
def health_check():
    return {"status": "online", "message": "Servidor AgroTech operacional"}

@app.post("/api/usuarios")
def salvar_usuario(usuario: UsuarioSchema):
    try:
        ref = rtdb.reference(f"users/{usuario.uid}")
        ref.set({
            "nome": usuario.nome,
            "email": usuario.email,
            "role": usuario.role
        })
        return {"success": True, "message": "Utilizador guardado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-role/{uid}")
def obter_perfil(uid: str):
    try:
        ref = rtdb.reference(f"users/{uid}")
        dados = ref.get()
        if not dados:
            return {"uid": uid, "role": "user", "nome": "Produtor"}
        return dados
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/manejo", status_code=status.HTTP_201_CREATED)
def criar_registro(registro: ManejoSchema):
    try:
        novo = registro.model_dump()
        novo["criadoEm"] = datetime.utcnow().isoformat()
        ref = rtdb.reference("registros_manejo")
        novo_node = ref.push(novo)
        novo["id"] = novo_node.key
        return {"success": True, "data": novo}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/users/{uid_alvo}")
def eliminar_utilizador(uid_alvo: str):
    try:
        rtdb.reference(f"users/{uid_alvo}").delete()
        return {"success": True, "message": "Utilizador eliminado com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/dashboard/{uid}")
def painel_admin(uid: str):
    user_ref = rtdb.reference(f"users/{uid}").get()
    role = user_ref.get("role") if isinstance(user_ref, dict) else "user"
    
    if role != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores.")

    usuarios = rtdb.reference("users").get() or {}
    manejo = rtdb.reference("registros_manejo").get() or {}

    return {
        "success": True,
        "metricas": {
            "total_usuarios": len(usuarios),
            "total_registros": len(manejo)
        },
        "usuarios_lista": usuarios,
        "registros_lista": manejo
    }
