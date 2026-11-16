from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Jarvis is awake and listening."}
