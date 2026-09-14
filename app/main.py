from fastapi import FastAPI

fast_app = FastAPI()


@fast_app.get("/ping")
def ping():
    return {"message": "pong"}
