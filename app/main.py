from fastapi import FastAPI
from app.routers import auth, tasks

app = FastAPI(title="SecureTask API", version="1.0.0")

app.include_router(auth.router)
app.include_router(tasks.router)

@app.get("/")
def health_check():
    return {"status": "SecureTask API running"}
