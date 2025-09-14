import email
from locale import strcoll
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI(
)
class Customer(BaseModel):
    id:int
    name:str
    email:str
    phone:Optional[str]
    address:Optional[strcoll]


#create 
customer_list= []
@app.post("/customers",response_model=Customer)
def create_customer(customer: Customer):
    customer_list.append(customer)
    return customer

#read 
@app.post("/customers",response_model=list[Customer])
def get_customer():
    return customer_list
#update
@app.put(f"/customers/{id}",response_model=Customer)
def update_customer(id:int,customer:Customer):
    for i ,existing_customer  in enumerate(customer_list):
        if existing_customer.id ==id:
            customer_list[i]=customer
            return customer
        raise HTTPException(status_code=404, detail="Customer not found")
#delete         
@app.delete(f"/customers/{id}",response_model=Customer)
def delete_customer(id:int,customer:Customer):
    for i ,existing_customer  in enumerate(customer_list):
        if existing_customer.id ==id:
            delete_customer=customer_list.pop(i)
            return customer
        raise HTTPException(status_code=404, detail="Customer not found")
        