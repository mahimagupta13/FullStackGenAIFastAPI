import streamlit as st
import requests

BASE_URL = "https://mahimagupta13-enrollmentapi.hf.space"  # Root API URL

st.set_page_config(page_title="CRM System", layout="wide")
st.title("📇 Customer Relationship Management System")

# Sidebar for operation selection
operation = st.sidebar.selectbox(   
    "Choose Operation",
    ["View Customers", "Create Customer", "Update Customer", "Delete Customer"]
)

# --------------------------
# Helper: fetch customers
# --------------------------
def fetch_customers():
    try:
        response = requests.get(f"{BASE_URL}/customers")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching customers: {e}")
    return []

# --------------------------
# View Customers
# --------------------------
if operation == "View Customers":
    st.subheader("📋 All Customers")
    if st.button("Refresh List"):
        customers = fetch_customers()
        if customers:
            st.table(customers)
        else:
            st.info("No customers found.")

# --------------------------
# Create Customer
# --------------------------
elif operation == "Create Customer":
    st.subheader("➕ Create Customer")
    create_id = st.number_input("Customer ID", min_value=1, step=1, key="create_id")
    create_name = st.text_input("Customer Name", key="create_name")
    create_email = st.text_input("Customer Email", key="create_email")
    create_phone = st.text_input("Customer Phone", key="create_phone")
    create_address = st.text_input("Customer Address", key="create_address")

    if st.button("Create Customer"):
        customer_data = {
            "id": create_id,
            "name": create_name,
            "email": create_email,
            "phone": create_phone,
            "address": create_address
        }
        response = requests.post(f"{BASE_URL}/customers", json=customer_data)
        if response.status_code == 200:
            st.success("✅ Customer created successfully")
        else:
            st.error(f"❌ Failed to create customer: {response.text}")

# --------------------------
# Update Customer
# --------------------------
elif operation == "Update Customer":
    st.subheader("✏️ Update Customer")
    customers = fetch_customers()

    if customers:
        selected = st.selectbox(
            "Select Customer to Update",
            options=[f"{c['id']} - {c['name']}" for c in customers]
        )
        selected_id = int(selected.split(" - ")[0])

        customer_data = next(c for c in customers if c["id"] == selected_id)
        update_name = st.text_input("New Name", value=customer_data["name"])
        update_email = st.text_input("New Email", value=customer_data["email"])
        update_phone = st.text_input("New Phone", value=customer_data.get("phone", ""))
        update_address = st.text_input("New Address", value=customer_data.get("address", ""))

        if st.button("Update Customer"):
            update_data = {
                "id": selected_id,
                "name": update_name,
                "email": update_email,
                "phone": update_phone,
                "address": update_address
            }
            response = requests.put(f"{BASE_URL}/customers/{selected_id}", json=update_data)
            if response.status_code == 200:
                st.success("✅ Customer updated successfully")
            else:
                st.error(f"❌ Failed to update customer: {response.text}")
    else:
        st.info("No customers available for update.")

# --------------------------
# Delete Customer
# --------------------------
elif operation == "Delete Customer":
    st.subheader("🗑️ Delete Customer")
    customers = fetch_customers()

    if customers:
        selected = st.selectbox(
            "Select Customer to Delete",
            options=[f"{c['id']} - {c['name']}" for c in customers]
        )
        selected_id = int(selected.split(" - ")[0])

        if st.button("Delete Customer"):
            response = requests.delete(f"{BASE_URL}/customers/{selected_id}")
            if response.status_code == 200:
                st.success(f"✅ Customer {selected_id} deleted successfully")
            else:
                st.error(f"❌ Failed to delete customer: {response.text}")
    else:
        st.info("No customers available for deletion.")
