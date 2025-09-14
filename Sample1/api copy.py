from pydantic import BaseModel
from fastapi import FastAPI

# This must exist
app = FastAPI()

# Request model
class Numbers(BaseModel):
    x: int
    y: int

# Route
@app.post("/add")
def add_numbers(numbers: Numbers):
    return {"result": numbers.x + numbers.y}

@app.post("/multiply")
def add_numbers(numbers: Numbers):
    return {"result": numbers.x * numbers.y}

@app.post("/del")
def add_numbers(numbers: Numbers):
    return {"result": numbers.x - numbers.y}

@app.post("/div")
def add_numbers(numbers: Numbers):
    return {"result": numbers.x / numbers.y}
