from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# FastAPI app
app = FastAPI()

class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None

# In-memory storage
customer_list = []

# Create
@app.post("/customers", response_model=Customer)
def create_customer(customer: Customer):
    customer_list.append(customer)
    return customer

# Read all
@app.get("/customers", response_model=list[Customer])
def get_customers():
    return customer_list

# Update
@app.put("/customers/{id}", response_model=Customer)
def update_customer(id: int, customer: Customer):
    for i, existing_customer in enumerate(customer_list):
        if existing_customer.id == id:
            customer_list[i] = customer
            return customer
    raise HTTPException(status_code=404, detail="Customer not found")

# Delete
@app.delete("/customers/{id}", response_model=Customer)
def delete_customer(id: int):
    for i, existing_customer in enumerate(customer_list):
        if existing_customer.id == id:
            deleted_customer = customer_list.pop(i)
            return deleted_customer
    raise HTTPException(status_code=404, detail="Customer not found")
