from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from firebase_config import db

router = APIRouter(prefix="/api/manejo", tags=["Manejo"])

class ManejoSchema(BaseModel):
    cultura: str
    tipo: str
    quantidade: Optional[str] = ""
    observacao: Optional[str] = ""

@router.get("/")
async def listar_registros():
    try:
        docs = (
            db.collection("registros_manejo")
            .order_by("criadoEm", direction=db.collection("registros_manejo").DESCENDING)
            .stream()
        )
        
        data = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            data.append(d)
            
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro no Firestore: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_registro(registro: ManejoSchema):
    try:
        novo_registro = registro.model_dump()
        novo_registro["criadoEm"] = datetime.utcnow().isoformat()

        _, doc_ref = db.collection("registros_manejo").add(novo_registro)
        novo_registro["id"] = doc_ref.id

        return {"success": True, "data": novo_registro}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar: {str(e)}"
        )
