from fastapi import FastAPI
from app.db.database import engine, Base
from app.routers import auth, tasks
from app.models.audit_log import AuditLog

app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def health_check():
    return {"status": "SecureTask API running"}