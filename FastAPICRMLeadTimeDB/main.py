from typing import Optional, List
from datetime import datetime
import json
import os
from supabase import create_client, Client
from typing import Any, Dict
import requests
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import re
load_dotenv(override=True)
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

#SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip().strip('"').strip("'")
#SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or "").strip().strip('"').strip("'")
GROQ_API_KEY="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"
SUPABASE_URL ="https://jobrlreqmtwnkociihcz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpvYnJscmVxbXR3bmtvY2lpaGN6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyODY1MzAsImV4cCI6MjA3Mzg2MjUzMH0.fQOjACZNu7htOQxrrOUaw0dMVrOYXPHx1SG25WaFlt8"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not configured. Endpoints will fail until set.")
else:
    print(f"Supabase URL in env: {SUPABASE_URL}")

supabase: Optional[Client] = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")

def _get_supabase() -> Client:
    global supabase, SUPABASE_URL, SUPABASE_KEY
    if supabase is not None:
        return supabase
    # Attempt lazy init using envs (support hot-setting without restart)
    SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip().strip('"').strip("'")
    SUPABASE_KEY = (os.getenv("SUPABASE_KEY") or "").strip().strip('"').strip("'")
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            return supabase
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize Supabase client: {e}")
    raise HTTPException(status_code=500, detail="Supabase client not initialized. Set SUPABASE_URL and SUPABASE_KEY.")

def _row_to_customer(row: dict) -> Customer:
    def parse_dt(value: Optional[str]) -> Optional[datetime]:
        if value is None or value == "":
            return None
        try:
            return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except Exception:
            return None
    return Customer(
        id=int(row.get('id')),
        name=str(row.get('name')),
        email=str(row.get('email')),
        phone=row.get('phone'),
        address=row.get('address'),
        country=row.get('country'),
        goal=row.get('goal'),
        budget=row.get('budget'),
        webinar_join=parse_dt(row.get('webinar_join')),
        webinar_leave=parse_dt(row.get('webinar_leave')),
        asked_q=bool(row.get('asked_q', False)),
        referred=bool(row.get('referred', False)),
        past_touchpoints=int(row.get('past_touchpoints', 0)),
        created_at=parse_dt(row.get('created_at')) or datetime.utcnow(),
        closed_at=parse_dt(row.get('closed_at')),
        engaged_mins=int(row['engaged_mins']) if row.get('engaged_mins') is not None and str(row.get('engaged_mins')) != '' else None,
        score=int(row['score']) if row.get('score') is not None and str(row.get('score')) != '' else None,
        reasoning=row.get('reasoning'),
        status=row.get('status'),
    )

def _customer_to_row(customer: Customer) -> dict:
    return {
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
        'created_at': customer.created_at.isoformat() if isinstance(customer.created_at, datetime) else customer.created_at,
        'closed_at': customer.closed_at.isoformat() if customer.closed_at else None,
        'engaged_mins': customer.engaged_mins,
        'score': customer.score,
        'reasoning': customer.reasoning,
        'status': customer.status,
    }

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
    client = _get_supabase()
    # Check if customer ID already exists
    try:
        resp = client.table("customers").select("id").eq("id", customer.id).execute()
        data = getattr(resp, 'data', None) or (resp.get('data') if isinstance(resp, dict) else None)
        if data and len(data) > 0:
            raise HTTPException(status_code=400, detail="Customer with this ID already exists")
        row = _customer_to_row(customer)
        ins = client.table("customers").insert(row).execute()
        _ = getattr(ins, 'data', None) or (ins.get('data') if isinstance(ins, dict) else None)
        return _with_lead_time(customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {e}")

# Read all
@app.get("/customers", response_model=list[CustomerOut])
def get_customers():
    client = _get_supabase()
    try:
        resp = client.table("customers").select("*").execute()
        rows = getattr(resp, 'data', None) or (resp.get('data') if isinstance(resp, dict) else [])
        customers: List[CustomerOut] = []
        for row in rows or []:
            customers.append(_with_lead_time(_row_to_customer(row)))
        return customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {e}")

# Read single customer
@app.get("/customers/{id}", response_model=CustomerOut)
def get_customer(id: int):
    client = _get_supabase()
    try:
        resp = client.table("customers").select("*").eq("id", id).execute()
        rows = getattr(resp, 'data', None) or (resp.get('data') if isinstance(resp, dict) else [])
        if not rows:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer = _row_to_customer(rows[0])
        return _with_lead_time(customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer: {e}")

# Update
@app.put("/customers/{id}", response_model=CustomerOut)
def update_customer(id: int, customer: Customer):
    client = _get_supabase()
    try:
        row = _customer_to_row(customer)
        upd = client.table("customers").update(row).eq("id", id).execute()
        data = getattr(upd, 'data', None) or (upd.get('data') if isinstance(upd, dict) else None)
        if data is None:
            # Some clients return empty data for update; verify existence
            chk = client.table("customers").select("id").eq("id", id).execute()
            chk_rows = getattr(chk, 'data', None) or (chk.get('data') if isinstance(chk, dict) else [])
            if not chk_rows:
                raise HTTPException(status_code=404, detail="Customer not found")
        return _with_lead_time(customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update customer: {e}")

# Delete
@app.delete("/customers/{id}", response_model=CustomerOut)
def delete_customer(id: int):
    client = _get_supabase()
    try:
        # Fetch the customer first for response
        resp = client.table("customers").select("*").eq("id", id).execute()
        rows = getattr(resp, 'data', None) or (resp.get('data') if isinstance(resp, dict) else [])
        if not rows:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer = _row_to_customer(rows[0])
        # Delete
        client.table("customers").delete().eq("id", id).execute()
        return _with_lead_time(customer)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete customer: {e}")


@app.get("/customers/{id}/lead-time")
def get_lead_time(id: int):
    client = _get_supabase()
    try:
        resp = client.table("customers").select("created_at, closed_at").eq("id", id).execute()
        rows = getattr(resp, 'data', None) or (resp.get('data') if isinstance(resp, dict) else [])
        if not rows:
            raise HTTPException(status_code=404, detail="Customer not found")
        tmp = _row_to_customer(rows[0])
        lead_days: Optional[int] = None
        if tmp.closed_at is not None:
            delta = tmp.closed_at - tmp.created_at
            lead_days = max(0, delta.days)
        return {"id": id, "lead_time_days": lead_days}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute lead time: {e}")


@app.post("/customers/{id}/qualify", response_model=CustomerOut)
def qualify_customer(id: int):
    client = _get_supabase()
    try:
        resp = client.table("customers").select("*").eq("id", id).execute()
        rows = getattr(resp, 'data', None) or (resp.get('data') if isinstance(resp, dict) else [])
        if not rows:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer = _row_to_customer(rows[0])
        qualified = _qualify_customer(customer)
        update_fields = {
            'engaged_mins': qualified.engaged_mins,
            'score': qualified.score,
            'reasoning': qualified.reasoning,
            'status': qualified.status,
        }
        client.table("customers").update(update_fields).eq("id", id).execute()
        return _with_lead_time(qualified)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to qualify customer: {e}")

# New endpoint to export all data as CSV
@app.get("/customers/export/csv")
def export_customers_csv():
    """Export all customers as CSV-like JSON array (no file I/O)"""
    client = _get_supabase()
    try:
        resp = client.table("customers").select("*").execute()
        rows = getattr(resp, 'data', None) or (resp.get('data') if isinstance(resp, dict) else [])
        if not rows:
            raise HTTPException(status_code=404, detail="No customers found")
        output = []
        for row in rows:
            customer = _row_to_customer(row)
            output.append({
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
            })
        return {"message": "Data exported successfully", "data": output}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {e}")

# New endpoint to get CSV file download
@app.get("/customers/download/csv")
def download_customers_csv():
    """Return customers as CSV string (no filesystem write)"""
    client = _get_supabase()
    try:
        resp = client.table("customers").select("*").execute()
        rows = getattr(resp, 'data', None) or (resp.get('data') if isinstance(resp, dict) else [])
        if not rows:
            raise HTTPException(status_code=404, detail="No customers found")
        # Build CSV string in-memory
        headers = [
            'id','name','email','phone','address','country','goal','budget','webinar_join','webinar_leave',
            'asked_q','referred','past_touchpoints','created_at','closed_at','engaged_mins','score','reasoning','status','lead_time_days'
        ]
        lines = [",".join(headers)]
        for row in rows:
            customer = _row_to_customer(row)
            values = [
                str(customer.id),
                (customer.name or '').replace(',', ' '),
                (customer.email or '').replace(',', ' '),
                (customer.phone or '').replace(',', ' '),
                (customer.address or '').replace(',', ' '),
                (customer.country or '').replace(',', ' '),
                (customer.goal or '').replace(',', ' '),
                (customer.budget or '').replace(',', ' '),
                customer.webinar_join.isoformat() if customer.webinar_join else '',
                customer.webinar_leave.isoformat() if customer.webinar_leave else '',
                'true' if customer.asked_q else 'false',
                'true' if customer.referred else 'false',
                str(customer.past_touchpoints),
                customer.created_at.isoformat(),
                customer.closed_at.isoformat() if customer.closed_at else '',
                '' if customer.engaged_mins is None else str(customer.engaged_mins),
                '' if customer.score is None else str(customer.score),
                (customer.reasoning or '').replace('\n', ' ').replace(',', ' '),
                (customer.status or ''),
                '' if _with_lead_time(customer).lead_time_days is None else str(_with_lead_time(customer).lead_time_days),
            ]
            lines.append(",".join(values))
        csv_content = "\n".join(lines)
        return {"filename": "customers.csv", "content_type": "text/csv", "content": csv_content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build CSV: {e}")
