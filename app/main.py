from db.database import Base, engine
from fastapi import FastAPI
from models.audit_log import AuditLog
from routers import auth, tasks

app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/")
def health_check():
    return {"status": "SecureTask API running"}
