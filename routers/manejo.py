from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from firebase_config import rtdb

router = APIRouter(prefix="/api/manejo", tags=["Manejo"])

class ManejoSchema(BaseModel):
    cultura: str
    tipo: str
    quantidade: Optional[str] = ""
    observacao: Optional[str] = ""

@router.get("/")
async def listar_registros():
    try:
        ref = rtdb.reference("registros_manejo")
        snapshot = ref.get()

        data = []
        if snapshot:
            for key, val in snapshot.items():
                val["id"] = key
                data.append(val)

        # Ordenar pelos mais recentes
        data.sort(key=lambda x: x.get("criadoEm", ""), reverse=True)
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no Realtime Database: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_registro(registro: ManejoSchema):
    try:
        novo_registro = registro.model_dump()
        novo_registro["criadoEm"] = datetime.utcnow().isoformat()

        # Insere um novo nó no Realtime Database usando push()
        ref = rtdb.reference("registros_manejo")
        novo_node = ref.push(novo_registro)
        novo_registro["id"] = novo_node.key

        return {"success": True, "data": novo_registro}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar no Realtime Database: {str(e)}"
        )
