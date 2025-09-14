import streamlit as st
import requests
from datetime import datetime

#BASE_URL = "http://127.0.0.1:8000"  # Changed from 8001 to 8000
BASE_URL = "https://mahimagupta13-enrollmentleadtime.hf.space"

st.set_page_config(page_title="CRM System", layout="wide")
st.title("📇 Customer Relationship Management System")

# --------------- Helpers ---------------
def fetch_customers():
    try:
        r = requests.get(f"{BASE_URL}/customers", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching customers: {e}")
        return []

def iso_or_none(dt_str: str):
    if not dt_str:
        return None
    try:
        # Accept many date formats; prefer full ISO if provided
        return datetime.fromisoformat(dt_str).isoformat()
    except Exception:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").isoformat()
        except Exception:
            try:
                return datetime.strptime(dt_str, "%Y-%m-%d").isoformat()
            except Exception:
                return None

def post_customer(payload):
    return requests.post(f"{BASE_URL}/customers", json=payload, timeout=15)

def put_customer(cid, payload):
    return requests.put(f"{BASE_URL}/customers/{cid}", json=payload, timeout=15)

def delete_customer(cid):
    return requests.delete(f"{BASE_URL}/customers/{cid}", timeout=10)

def get_lead_time(cid):
    return requests.get(f"{BASE_URL}/customers/{cid}/lead-time", timeout=10)

def qualify_customer(cid):
    return requests.post(f"{BASE_URL}/customers/{cid}/qualify", timeout=30)

# --------------- UI ---------------
section = st.sidebar.selectbox(
    "Choose Operation",
    ["View Customers", "Create Customer", "Update Customer", "Delete Customer", "Qualify Customer"]
)

# View
if section == "View Customers":
    st.subheader("📋 All Customers")
    if st.button("Refresh"):
        data = fetch_customers()
        if data:
            st.dataframe(data, use_container_width=True)
        else:
            st.info("No customers found.")

    with st.expander("Lead time for a specific customer"):
        cid = st.number_input("Customer ID", min_value=1, step=1, key="view_lead_id")
        if st.button("Get Lead Time"):
            resp = get_lead_time(cid)
            if resp.status_code == 200:
                st.success(resp.json())
            else:
                st.error(resp.text)

# Create
elif section == "Create Customer":
    st.subheader("➕ Create Customer")
    c1, c2, c3 = st.columns(3)
    with c1:
        create_id = st.number_input("ID", min_value=1, step=1, key="create_id")
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone", value="")
    with c2:
        address = st.text_input("Address", value="")
        country = st.text_input("Country", value="")
        goal = st.text_input("Goal", value="")
        budget = st.selectbox("Budget", ["", "Company", "Self"])
    with c3:
        webinar_join = st.text_input("Webinar Join (ISO or YYYY-MM-DD HH:MM:SS)", value="")
        webinar_leave = st.text_input("Webinar Leave (ISO or YYYY-MM-DD HH:MM:SS)", value="")
        asked_q = st.checkbox("Asked Question", value=False)
        referred = st.checkbox("Referred", value=False)
        past_touchpoints = st.number_input("Past Touchpoints", min_value=0, step=1, value=0)

    if st.button("Create"):
        payload = {
            "id": int(create_id),
            "name": name,
            "email": email,
            "phone": phone or None,
            "address": address or None,
            "country": country or None,
            "goal": goal or None,
            "budget": budget or None if budget else None,
            "webinar_join": iso_or_none(webinar_join),
            "webinar_leave": iso_or_none(webinar_leave),
            "asked_q": bool(asked_q),
            "referred": bool(referred),
            "past_touchpoints": int(past_touchpoints),
        }
        resp = post_customer(payload)
        if resp.status_code == 200:
            st.success("✅ Customer created")
            st.json(resp.json())
        else:
            st.error(resp.text)

# Update
elif section == "Update Customer":
    st.subheader("✏️ Update Customer (replaces full record)")
    customers = fetch_customers()
    if not customers:
        st.info("No customers available to update.")
    else:
        selected = st.selectbox("Select customer", [f"{c['id']} - {c['name']}" for c in customers])
        cid = int(selected.split(" - ")[0])
        current = next(c for c in customers if c["id"] == cid)

        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Name", value=current.get("name",""))
            email = st.text_input("Email", value=current.get("email",""))
            phone = st.text_input("Phone", value=current.get("phone","") or "")
        with c2:
            address = st.text_input("Address", value=current.get("address","") or "")
            country = st.text_input("Country", value=current.get("country","") or "")
            goal = st.text_input("Goal", value=current.get("goal","") or "")
            budget = st.selectbox("Budget", ["", "Company", "Self"], index=(["","Company","Self"].index(current.get("budget","") or "")))
        with c3:
            webinar_join = st.text_input("Webinar Join (ISO)", value=current.get("webinar_join","") or "")
            webinar_leave = st.text_input("Webinar Leave (ISO)", value=current.get("webinar_leave","") or "")
            asked_q = st.checkbox("Asked Question", value=bool(current.get("asked_q", False)))
            referred = st.checkbox("Referred", value=bool(current.get("referred", False)))
            past_touchpoints = st.number_input("Past Touchpoints", min_value=0, step=1, value=int(current.get("past_touchpoints", 0)))

        if st.button("Update"):
            payload = {
                "id": cid,
                "name": name,
                "email": email,
                "phone": phone or None,
                "address": address or None,
                "country": country or None,
                "goal": goal or None,
                "budget": budget or None if budget else None,
                "webinar_join": iso_or_none(webinar_join),
                "webinar_leave": iso_or_none(webinar_leave),
                "asked_q": bool(asked_q),
                "referred": bool(referred),
                "past_touchpoints": int(past_touchpoints),
                # Optional server-computed fields can be omitted on update:
                "created_at": current.get("created_at"),
                "closed_at": current.get("closed_at"),
                "engaged_mins": current.get("engaged_mins"),
                "score": current.get("score"),
                "reasoning": current.get("reasoning"),
                "status": current.get("status"),
            }
            resp = put_customer(cid, payload)
            if resp.status_code == 200:
                st.success("✅ Customer updated")
                st.json(resp.json())
            else:
                st.error(resp.text)

# Delete
elif section == "Delete Customer":
    st.subheader("🗑️ Delete Customer")
    customers = fetch_customers()
    if not customers:
        st.info("No customers available to delete.")
    else:
        selected = st.selectbox("Select customer", [f"{c['id']} - {c['name']}" for c in customers])
        cid = int(selected.split(" - ")[0])
        if st.button("Delete"):
            resp = delete_customer(cid)
            if resp.status_code == 200:
                st.success(f"✅ Deleted {cid}")
                st.json(resp.json())
            else:
                st.error(resp.text)

# Qualify
elif section == "Qualify Customer":
    st.subheader("⭐ Qualify Customer (Groq)")
    customers = fetch_customers()
    if not customers:
        st.info("No customers available to qualify.")
    else:
        selected = st.selectbox("Select customer", [f"{c['id']} - {c['name']}" for c in customers], key="qual_select")
        cid = int(selected.split(" - ")[0])

        if st.button("Run Qualification"):
            resp = qualify_customer(cid)
            if resp.status_code == 200:
                result = resp.json()
                st.success("Qualified")
                # Show key outputs from the backend model
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Score", result.get("score"))
                with k2:
                    st.metric("Status", result.get("status"))
                with k3:
                    st.metric("Engaged Mins", result.get("engaged_mins"))
                with k4:
                    st.metric("Lead Time (days)", result.get("lead_time_days"))
                st.write("Reasoning")
                st.write(result.get("reasoning"))
                st.write("Full record")
                st.json(result)
            else:
                st.error(resp.text)
