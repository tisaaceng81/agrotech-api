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

if firebase_credentials_raw:
    try:
        raw_str = firebase_credentials_raw.strip().strip('"').strip("'")
        cred_dict = json.loads(raw_str)
    except Exception as e:
        print(f"Erro ao ler FIREBASE_CREDENTIALS: {e}")
        cred_dict = None

if not cred_dict:
    cred_dict = {
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", ""),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }

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
    description="Backend FastAPI com Autenticação e Aprovação",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterSchema(BaseModel):
    nome: str
    email: str
    senha: str

class LoginSchema(BaseModel):
    email: str
    senha: str

class ManejoSchema(BaseModel):
    cultura: str
    area: str
    tipo: str
    quantidade: str
    observacao: Optional[str] = ""
    uid_usuario: str

@app.get("/health")
def health_check():
    return {"status": "online", "message": "Servidor AgroTech operacional"}

@app.post("/api/register")
def registar_utilizador(dados: RegisterSchema):
    try:
        users_ref = rtdb.reference("users")
        all_users = users_ref.get() or {}
        
        # Verificar se o e-mail já existe
        for uid_key, u_data in all_users.items():
            if isinstance(u_data, dict) and u_data.get("email") == dados.email:
                raise HTTPException(status_code=400, detail="Este e-mail já está registado.")

        # Se não houver nenhum utilizador, o primeiro é ADMIN aprovado automaticamente
        is_first = len(all_users) == 0
        role = "admin" if is_first else "user"
        status_conta = "approved" if is_first else "pending"

        novo_ref = users_ref.push()
        uid = novo_ref.key

        novo_ref.set({
            "uid": uid,
            "nome": dados.nome,
            "email": dados.email,
            "senha": dados.senha,
            "role": role,
            "status": status_conta,
            "criadoEm": datetime.utcnow().isoformat()
        })

        return {
            "success": True, 
            "message": "Conta criada com sucesso!" if not is_first else "Admin Master criado com sucesso!",
            "status": status_conta
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
def fazer_login(dados: LoginSchema):
    try:
        users_ref = rtdb.reference("users")
        all_users = users_ref.get() or {}

        user_encontrado = None
        for uid_key, u_data in all_users.items():
            if isinstance(u_data, dict) and u_data.get("email") == dados.email:
                if u_data.get("senha") == dados.senha:
                    user_encontrado = u_data
                    break

        if not user_encontrado:
            raise HTTPException(status_code=401, detail="E-mail ou palavra-passe incorretos.")

        if user_encontrado.get("status") == "pending":
            raise HTTPException(status_code=403, detail="A sua conta está pendente de aprovação pelo Administrador.")

        return {
            "success": True,
            "uid": user_encontrado.get("uid"),
            "nome": user_encontrado.get("nome"),
            "role": user_encontrado.get("role"),
            "status": user_encontrado.get("status")
        }
    except HTTPException as he:
        raise he
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

@app.patch("/api/admin/users/{uid_alvo}/status")
def alterar_status_utilizador(uid_alvo: str, status_payload: dict):
    try:
        novo_status = status_payload.get("status") # 'approved' ou 'rejected'
        ref = rtdb.reference(f"users/{uid_alvo}")
        if not ref.get():
            raise HTTPException(status_code=404, detail="Utilizador não encontrado.")
        ref.update({"status": novo_status})
        return {"success": True, "message": f"Estado alterado para {novo_status}."}
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
    user_ref = rtdb.reference(f"users/{uid}").get() or {}
    role = user_ref.get("role", "user")
    
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
