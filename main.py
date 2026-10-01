import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import manejo

app = FastAPI(
    title="API AgroTech",
    description="Backend Python FastAPI para Flutter com Firestore",
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

app.include_router(manejo.router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
