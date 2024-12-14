from fastapi import FastAPI
from routes import router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "ok"}

app.include_router(router, tags=["football"])
