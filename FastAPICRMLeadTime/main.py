from typing import Optional, List
from datetime import datetime
import json
import os
import csv
import pandas as pd
from typing import Any, Dict
import requests
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import re
load_dotenv(override=True)
print( os.getenv("GROQ_API_KEY"))
# FastAPI app
app = FastAPI()

# Enable CORS for local development and browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Customer(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    goal: Optional[str] = None  # e.g. "Become AI PM", "Run AI Startup"
    budget: Optional[str] = None  # "Company" / "Self"
    webinar_join: Optional[datetime] = None
    webinar_leave: Optional[datetime] = None
    asked_q: bool = False  # Engaged in Q&A
    referred: bool = False  # Alumni/partner referral
    past_touchpoints: int = 0  # Downloads, visits
    created_at: datetime = datetime.utcnow()
    closed_at: Optional[datetime] = None

    # Derived qualification fields
    engaged_mins: Optional[int] = None
    score: Optional[int] = None  # 0–100
    reasoning: Optional[str] = None
    status: Optional[str] = None  # "Qualified" / "Nurture"


class CustomerOut(Customer):
    lead_time_days: Optional[int] = None

# CSV file path
CSV_FILE = "customers.csv"

def load_customers_from_csv() -> List[Customer]:
    """Load customers from CSV file"""
    if not os.path.exists(CSV_FILE):
        return []
    
    customers = []
    try:
        df = pd.read_csv(CSV_FILE)
        for _, row in df.iterrows():
            # Convert string dates back to datetime objects
            webinar_join = None
            webinar_leave = None
            created_at = None
            closed_at = None
            
            if pd.notna(row.get('webinar_join')):
                webinar_join = datetime.fromisoformat(row['webinar_join'].replace('Z', '+00:00'))
            if pd.notna(row.get('webinar_leave')):
                webinar_leave = datetime.fromisoformat(row['webinar_leave'].replace('Z', '+00:00'))
            if pd.notna(row.get('created_at')):
                created_at = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
            if pd.notna(row.get('closed_at')):
                closed_at = datetime.fromisoformat(row['closed_at'].replace('Z', '+00:00'))
            
            customer = Customer(
                id=int(row['id']),
                name=str(row['name']),
                email=str(row['email']),
                phone=row.get('phone') if pd.notna(row.get('phone')) else None,
                address=row.get('address') if pd.notna(row.get('address')) else None,
                country=row.get('country') if pd.notna(row.get('country')) else None,
                goal=row.get('goal') if pd.notna(row.get('goal')) else None,
                budget=row.get('budget') if pd.notna(row.get('budget')) else None,
                webinar_join=webinar_join,
                webinar_leave=webinar_leave,
                asked_q=bool(row.get('asked_q', False)),
                referred=bool(row.get('referred', False)),
                past_touchpoints=int(row.get('past_touchpoints', 0)),
                created_at=created_at or datetime.utcnow(),
                closed_at=closed_at,
                engaged_mins=int(row['engaged_mins']) if pd.notna(row.get('engaged_mins')) else None,
                score=int(row['score']) if pd.notna(row.get('score')) else None,
                reasoning=row.get('reasoning') if pd.notna(row.get('reasoning')) else None,
                status=row.get('status') if pd.notna(row.get('status')) else None
            )
            customers.append(customer)
    except Exception as e:
        print(f"Error loading customers from CSV: {e}")
        return []
    
    return customers

def save_customers_to_csv(customers: List[Customer]):
    """Save customers to CSV file"""
    if not customers:
        return
    
    # Convert customers to list of dictionaries
    data = []
    for customer in customers:
        row = {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
            'country': customer.country,
            'goal': customer.goal,
            'budget': customer.budget,
            'webinar_join': customer.webinar_join.isoformat() if customer.webinar_join else None,
            'webinar_leave': customer.webinar_leave.isoformat() if customer.webinar_leave else None,
            'asked_q': customer.asked_q,
            'referred': customer.referred,
            'past_touchpoints': customer.past_touchpoints,
            'created_at': customer.created_at.isoformat(),
            'closed_at': customer.closed_at.isoformat() if customer.closed_at else None,
            'engaged_mins': customer.engaged_mins,
            'score': customer.score,
            'reasoning': customer.reasoning,
            'status': customer.status
        }
        data.append(row)
    
    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv(CSV_FILE, index=False)

# Load customers from CSV on startup
customer_list: List[Customer] = load_customers_from_csv()

def _with_lead_time(customer: Customer) -> CustomerOut:
    lead_days: Optional[int] = None
    if customer.closed_at is not None:
        delta = customer.closed_at - customer.created_at
        lead_days = max(0, delta.days)
    return CustomerOut(**customer.dict(), lead_time_days=lead_days)


def _compute_engaged_minutes(customer: Customer) -> Optional[int]:
    if customer.webinar_join is None or customer.webinar_leave is None:
        return None
    if customer.webinar_leave < customer.webinar_join:
        return 0
    delta = customer.webinar_leave - customer.webinar_join
    return int(delta.total_seconds() // 60)


def _build_few_shot_prompt(customer: Customer, engaged_mins: Optional[int]) -> str:
    rubric = (
        "You are a Lead Qualification Engine for 100xEngineers. Assess fit (0-50) and intent (0-50) "
        "and return a total score (0-100) with concise reasoning and a status: Qualified or Nurture.\n\n"
        "Fit factors: goal alignment, budget readiness (Company > Self), referral presence, geography relevance.\n"
        "Intent factors: webinar engagement minutes, interaction (asked questions), past touchpoints, post-webinar action signals.\n\n"
        "Scoring bands: 80-100 Strongly Qualified; 60-79 Qualified; 40-59 Nurture; <40 Disqualified (map to Nurture).\n"
    )

    few_shots = [
        {
            "input": {
                "id": 1,
                "name": "Aditi Sharma",
                "goal": "Become AI Product Manager",
                "budget": "Company",
                "country": "India",
                "webinar_join": "2025-09-10T15:00:00",
                "webinar_leave": "2025-09-10T16:25:00",
                "asked_q": True,
                "referred": True,
                "past_touchpoints": 3,
            },
            "output": {
                "engaged_mins": 85,
                "score": 92,
                "reasoning": "Strong fit (goal aligns with program, company-funded, referral). High intent (85 mins attended, asked question, 3 prior touchpoints).",
                "status": "Qualified",
            },
        },
        {
            "input": {
                "id": 2,
                "name": "John Lee",
                "goal": "Explore AI for my startup",
                "budget": "Self",
                "country": "USA",
                "webinar_join": "2025-09-10T15:05:00",
                "webinar_leave": "2025-09-10T15:45:00",
                "asked_q": False,
                "referred": False,
                "past_touchpoints": 1,
            },
            "output": {
                "engaged_mins": 40,
                "score": 68,
                "reasoning": "Good fit (entrepreneurial goal, willing to self-fund). Medium intent (40 mins engaged, no Qs asked, 1 prior touchpoint).",
                "status": "Qualified",
            },
        },
        {
            "input": {
                "id": 3,
                "name": "Maria Gonzales",
                "goal": "Just exploring AI trends",
                "budget": "Self",
                "country": "Mexico",
                "webinar_join": "2025-09-10T15:20:00",
                "webinar_leave": "2025-09-10T15:40:00",
                "asked_q": False,
                "referred": False,
                "past_touchpoints": 0,
            },
            "output": {
                "engaged_mins": 20,
                "score": 38,
                "reasoning": "Weak fit (unclear career goal, self-funded). Low intent (20 mins attended, no interactions, no prior touchpoints).",
                "status": "Nurture",
            },
        },
    ]

    user_example: Dict[str, Any] = {
        "id": customer.id,
        "name": customer.name,
        "goal": customer.goal,
        "budget": customer.budget,
        "country": customer.country,
        "webinar_join": customer.webinar_join.isoformat() if customer.webinar_join else None,
        "webinar_leave": customer.webinar_leave.isoformat() if customer.webinar_leave else None,
        "asked_q": customer.asked_q,
        "referred": customer.referred,
        "past_touchpoints": customer.past_touchpoints,
    }

    prompt = (
        rubric
        + "Few-shot examples (JSON):\n"
        + json.dumps(few_shots, ensure_ascii=False)
        + "\n\nNow score this customer (JSON with keys: engaged_mins, score, reasoning, status).\n"
        + json.dumps(user_example, ensure_ascii=False)
    )
    return prompt


def _extract_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        # Try to find the first JSON object in the text
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            return json.loads(m.group(0))
        raise


def _call_groq_completion(prompt: str) -> Dict[str, Any]:
    api_key = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "You are a precise scoring engine. Return ONLY a compact JSON object with keys: engaged_mins, score, reasoning, status.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 512
        # If 400 errors persist without this, try adding:
        # "response_format": {"type": "json_object"}
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        try:
            return _extract_json(content)
        except Exception as parse_err:
            raise HTTPException(
                status_code=502,
                detail=f"Groq parsing failed: {parse_err}. Raw: {content[:500]}"
            )
    except requests.HTTPError as e:
        body_txt = e.response.text if getattr(e, "response", None) else ""
        raise HTTPException(status_code=502, detail=f"Groq API error: {e} - {body_txt}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq processing failed: {e}")


def _qualify_customer(customer: Customer) -> Customer:
    engaged = _compute_engaged_minutes(customer)
    customer.engaged_mins = engaged
    prompt = _build_few_shot_prompt(customer, engaged)
    result = _call_groq_completion(prompt)

    # Defensive parsing
    customer.score = int(max(0, min(100, int(result.get("score", 0)))))
    customer.reasoning = str(result.get("reasoning", ""))
    raw_status = str(result.get("status", "Nurture")).strip()
    customer.status = "Qualified" if raw_status.lower().startswith("qual") or customer.score >= 60 else "Nurture"
    # If LLM provided engaged_mins, favor it when present
    try:
        llm_engaged = result.get("engaged_mins")
        if isinstance(llm_engaged, (int, float)):
            customer.engaged_mins = int(llm_engaged)
    except Exception:
        pass
    return customer

# Create
@app.post("/customers", response_model=CustomerOut)
def create_customer(customer: Customer):
    # Check if customer ID already exists
    for existing_customer in customer_list:
        if existing_customer.id == customer.id:
            raise HTTPException(status_code=400, detail="Customer with this ID already exists")
    
    customer_list.append(customer)
    save_customers_to_csv(customer_list)
    return _with_lead_time(customer)

# Read all
@app.get("/customers", response_model=list[CustomerOut])
def get_customers():
    return [_with_lead_time(c) for c in customer_list]

# Read single customer
@app.get("/customers/{id}", response_model=CustomerOut)
def get_customer(id: int):
    for customer in customer_list:
        if customer.id == id:
            return _with_lead_time(customer)
    raise HTTPException(status_code=404, detail="Customer not found")

# Update
@app.put("/customers/{id}", response_model=CustomerOut)
def update_customer(id: int, customer: Customer):
    for i, existing_customer in enumerate(customer_list):
        if existing_customer.id == id:
            customer_list[i] = customer
            save_customers_to_csv(customer_list)
            return _with_lead_time(customer)
    raise HTTPException(status_code=404, detail="Customer not found")

# Delete
@app.delete("/customers/{id}", response_model=CustomerOut)
def delete_customer(id: int):
    for i, existing_customer in enumerate(customer_list):
        if existing_customer.id == id:
            deleted_customer = customer_list.pop(i)
            save_customers_to_csv(customer_list)
            return _with_lead_time(deleted_customer)
    raise HTTPException(status_code=404, detail="Customer not found")


@app.get("/customers/{id}/lead-time")
def get_lead_time(id: int):
    for customer in customer_list:
        if customer.id == id:
            lead_days: Optional[int] = None
            if customer.closed_at is not None:
                delta = customer.closed_at - customer.created_at
                lead_days = max(0, delta.days)
            return {"id": id, "lead_time_days": lead_days}
    raise HTTPException(status_code=404, detail="Customer not found")


@app.post("/customers/{id}/qualify", response_model=CustomerOut)
def qualify_customer(id: int):
    for i, customer in enumerate(customer_list):
        if customer.id == id:
            qualified = _qualify_customer(customer)
            customer_list[i] = qualified
            save_customers_to_csv(customer_list)
            return _with_lead_time(qualified)
    raise HTTPException(status_code=404, detail="Customer not found")

# New endpoint to export all data as CSV
@app.get("/customers/export/csv")
def export_customers_csv():
    """Export all customers as CSV file"""
    if not customer_list:
        raise HTTPException(status_code=404, detail="No customers found")
    
    # Create CSV content
    output = []
    for customer in customer_list:
        row = {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone or '',
            'address': customer.address or '',
            'country': customer.country or '',
            'goal': customer.goal or '',
            'budget': customer.budget or '',
            'webinar_join': customer.webinar_join.isoformat() if customer.webinar_join else '',
            'webinar_leave': customer.webinar_leave.isoformat() if customer.webinar_leave else '',
            'asked_q': customer.asked_q,
            'referred': customer.referred,
            'past_touchpoints': customer.past_touchpoints,
            'created_at': customer.created_at.isoformat(),
            'closed_at': customer.closed_at.isoformat() if customer.closed_at else '',
            'engaged_mins': customer.engaged_mins or '',
            'score': customer.score or '',
            'reasoning': customer.reasoning or '',
            'status': customer.status or '',
            'lead_time_days': _with_lead_time(customer).lead_time_days or ''
        }
        output.append(row)
    
    return {"message": "CSV data exported successfully", "data": output}

# New endpoint to get CSV file download
@app.get("/customers/download/csv")
def download_customers_csv():
    """Download customers as CSV file"""
    if not customer_list:
        raise HTTPException(status_code=404, detail="No customers found")
    
    # Save current data to CSV
    save_customers_to_csv(customer_list)
    
    return {"message": f"CSV file saved as {CSV_FILE}", "file_path": CSV_FILE}
