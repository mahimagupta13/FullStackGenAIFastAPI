from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI(
    title="Arithmetic API",
    description="Full-stack calculator API: Add, Subtract, Multiply, Divide",
    version="1.0.0"
)

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class Numbers(BaseModel):
    x: float
    y: float

# Routes
@app.post("/add")
def add(numbers: Numbers):
    return {"result": numbers.x + numbers.y}

@app.post("/subtract")
def subtract(numbers: Numbers):
    return {"result": numbers.x - numbers.y}

@app.post("/multiply")
def multiply(numbers: Numbers):
    return {"result": numbers.x * numbers.y}

@app.post("/divide")
def divide(numbers: Numbers):
    if numbers.y == 0:
        return {"error": "Division by zero is not allowed."}
    return {"result": numbers.x / numbers.y}
