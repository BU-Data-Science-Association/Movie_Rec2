from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
@app.get("/hello")
def hello():
    return {"message": "Hello from FastAPI!"}

# Example route: Get cards
@app.get("/cards")
def get_cards():
    return [
        {
            "id": 1,
            "image": "https://via.placeholder.com/400x500/FF6B6B/FFFFFF?text=Movie+1",
            "title": "Movie 1",
            "description": "An amazing movie you might like!",
        },
        {
            "id": 2,
            "image": "https://via.placeholder.com/400x500/4ECDC4/FFFFFF?text=Movie+2",
            "title": "Movie 2",
            "description": "Another great film recommendation.",
        },
    ]

# Example route: Record swipe
@app.post("/swipe")
def record_swipe(data: dict):
    print(f"Received swipe: {data}")
    return {"success": True}

