import os
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from routers import manejo
from firebase_config import rtdb

app = FastAPI(
    title="API AgroTech",
    description="Backend Python FastAPI para Flutter com Firebase",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "online", "message": "Servidor rodando perfeitamente"}

# Roteador de Manejo (Original)
app.include_router(manejo.router)
# Suporte adicional para chamadas com o prefixo /api (usado pelo Flutter)
app.include_router(manejo.router, prefix="/api")


# --- INTEGRAÇÃO DE PERFIL DE USUÁRIO E PAINEL ADMIN ---

@app.get("/api/user-role/{uid}")
@app.get("/user-role/{uid}")
def get_user_role(uid: str):
    """
    Retorna o perfil/função do usuário pelo UID do Firebase.
    """
    try:
        user_ref = rtdb.reference(f"users/{uid}")
        user_data = user_ref.get()

        if not user_data:
            role_ref = rtdb.reference(f"roles/{uid}")
            user_data = role_ref.get()

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )

        if isinstance(user_data, str):
            return {"uid": uid, "role": user_data}

        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar perfil do usuário: {str(e)}"
        )


@app.get("/api/admin/dashboard/{uid}")
@app.get("/admin/dashboard/{uid}")
def get_admin_dashboard(uid: str):
    """
    Verifica se o usuário é administrador e retorna dados do painel admin.
    """
    try:
        user_ref = rtdb.reference(f"users/{uid}")
        user_data = user_ref.get()

        role = None
        if isinstance(user_data, dict):
            role = user_data.get("role")
        elif isinstance(user_data, str):
            role = user_data

        if not role:
            role_ref = rtdb.reference(f"roles/{uid}")
            role_data = role_ref.get()
            if isinstance(role_data, str):
                role = role_data
            elif isinstance(role_data, dict):
                role = role_data.get("role")

        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: Perfil sem privilégios de Administrador."
            )

        # Consulta dados para exibição no Dashboard Admin
        manejo_ref = rtdb.reference("manejo")
        manejo_data = manejo_ref.get() or {}

        users_ref = rtdb.reference("users")
        users_data = users_ref.get() or {}

        total_manejo = len(manejo_data) if isinstance(manejo_data, (dict, list)) else 0
        total_users = len(users_data) if isinstance(users_data, (dict, list)) else 0

        return {
            "status": "success",
            "role": "admin",
            "total_registros_manejo": total_manejo,
            "total_usuarios": total_users,
            "message": "Acesso concedido ao painel do administrador."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar dados do admin: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
