from fastapi import FastAPI

app = FastAPI()

# API routes
@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI!"}
