from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from firebase_config import rtdb

router = APIRouter(prefix="/api", tags=["Autenticação e Perfis"])

class UsuarioSchema(BaseModel):
    uid: str
    nome: str
    email: str
    role: Optional[str] = "user"  # "user" ou "admin"

@router.post("/usuarios")
async def cadastrar_usuario(usuario: UsuarioSchema):
    try:
        ref = rtdb.reference(f"usuarios/{usuario.uid}")
        ref.set({
            "nome": usuario.nome,
            "email": usuario.email,
            "role": usuario.role
        })
        return {"success": True, "message": "Usuário salvo com sucesso."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar usuário: {str(e)}"
        )

@router.get("/user-role/{uid}")
async def obter_perfil(uid: str):
    try:
        ref = rtdb.reference(f"usuarios/{uid}")
        dados = ref.get()
        if not dados:
            raise HTTPException(status_code=404, detail="Usuário não localizado.")
        
        return {
            "uid": uid,
            "nome": dados.get("nome", ""),
            "email": dados.get("email", ""),
            "role": dados.get("role", "user")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar perfil: {str(e)}"
        )

@router.get("/admin/dashboard/{uid}")
async def obter_painel_admin(uid: str):
    user_ref = rtdb.reference(f"usuarios/{uid}").get()
    
    if not user_ref or user_ref.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Perfil sem privilégios de Administrador."
        )

    total_usuarios = len(rtdb.reference("usuarios").get() or {})
    total_manejos = len(rtdb.reference("registros_manejo").get() or {})

    return {
        "status": "sucesso",
        "metricas": {
            "total_usuarios": total_usuarios,
            "total_registros": total_manejos
        }
    }
