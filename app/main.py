from fastapi import FastAPI
from db.database import engine, Base
from routers import auth, tasks
from models.audit_log import AuditLog

app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def health_check():
    return {"status": "SecureTask API running"}