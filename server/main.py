from decouple import config
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    app_name = config("APP_NAME")
    return {"status": "ok", "app_name": app_name}
