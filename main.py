
from fastapi import FastAPI
from api.upload_api import router as upload_router
from api.chat_api import router as chat_router

app = FastAPI(title="Audit AI System")

app.include_router(upload_router, prefix="/upload", tags=["upload"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])

@app.get("/")
def root():
    return {"status": "Audit AI backend running"}
