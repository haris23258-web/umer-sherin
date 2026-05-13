import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. DATABASE CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Secrets missing! Please add SUPABASE_URL and SUPABASE_KEY in Streamlit settings.")
    st.stop()

# --- 2. UI CONFIGURATION ---
st.set_page_config(page_title="Pindi-Isloo Real Estate ERP", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 Estate Manager v1.1")
st.sidebar.info("Twin Cities Edition (Pindi/Islamabad)")
menu = ["📊 Dashboard", "🏠 Add Property", "👥 Client Desk & Match", "📋 View Inventory"]
choice = st.sidebar.radio("Navigate", menu)

# --- 4. DASHBOARD LOGIC ---
if choice == "📊 Dashboard":
    st.title("Main Dashboard")
    
    # Efficient count fetching
    inv_count = supabase.table("inventory").select("*", count="exact").execute()
    cli_count = supabase.table("clients").select("*", count="exact").execute()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Properties", inv_count.count if inv_count.count else 0)
    col2.metric("Active Clients", cli_count.count if cli_count.count else 0)
    col3.metric("Office Status", "Online 🟢")
    
    st.divider()
    st.subheader("Quick Links")
    c1, c2 = st.columns(2)
    if c1.button("Add New Property"):
        st.info("Navigate to 'Add Property' from the sidebar.")
    if c2.button("Run Smart Match"):
        st.info("Navigate to 'Client Desk' to see matches.")

# --- 5. ADD PROPERTY ---
elif choice == "🏠 Add Property":
    st.title("Register New Property")
    with st.form("property_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        p_type = c1.selectbox("Deal Type", ["Rent", "Sale"])
        area = c2.text_input("Area (e.g. G-11, Bahria Phase 7, Saddar)")
        
        c3, c4, c5 = st.columns(3)
        price = c3.number_input("Price (PKR)", min_value=0, step=5000)
        beds = c4.number_input("Beds", min_value=0, max_value=20)
        marla = c5.number_input("Marla/Kanal Size", min_value=0.5)
        
        portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Plot", "Apartment"])
        
        st.subheader("Owner Details (Confidential)")
        o_name = st.text_input("Owner Name")
        o_phone = st.text_input("Owner Contact Number")
        
        if st.form_submit_button("Save to Inventory"):
            if area and o_name:
                data = {
                    "property_type": p_type, "area": area, "price": price, 
                    "beds": beds, "marla": marla, "portion": portion,
                    "owner_name": o_name, "owner_contact": o_phone,
                    "status": "Available"
                }
                supabase.table("inventory").insert(data).execute()
                st.success(f"Property in {area} registered successfully!")
            else:
                st.error("Please fill in the Area and Owner details.")

# --- 6. CLIENT DESK & SMART MATCH ---
elif choice == "👥 Client Desk & Match":
    st.title("Client Relationship Management")
    tab1, tab2 = st.tabs(["🆕 Add New Client", "🎯 Find Matches"])
    
    with tab1:
        with st.form("client_reg"):
            cn = st.text_input("Client Name")
            cp = st.text_input("Phone Number")
            ct = st.selectbox("Requirement", ["Rent", "Sale"])
            cb = st.number_input("Max Budget (PKR)")
            ca = st.text_input("Preferred Area")
            
            if st.form_submit_button("Save Client"):
                supabase.table("clients").insert({
                    "client_name": cn, "phone_number": cp, 
                    "requirement_type": ct, "budget_max": cb, "area_preference": ca
                }).execute()
                st.success(f"Requirement saved for {cn}!")

    with tab2:
        clients_resp = supabase.table("clients").select("*").execute()
        clients = clients_resp.data
        if clients:
            target_name = st.selectbox("Select Client", [c['client_name'] for c in clients])
            c_data = next(x for x in clients if x['client_name'] == target_name)
            
            # Smart Matching Logic
            matches = supabase.table("inventory").select("*")\
                .eq("property_type", c_data['requirement_type'])\
                .lte("price", c_data['budget_max'])\
                .execute().data
            
            if matches:
                st.info(f"Found {len(matches)} properties matching {target_name}'s budget.")
                for m in matches:
                    with st.expander(f"🏠 {m['area']} - {m['price']:,} PKR"):
                        st.write(f"**Contact:** {m['owner_contact']}")
                        st.write(f"**Details:** {m['beds']} Beds | {m['marla']} Marla | {m['portion']}")
                        st.write(f"**Status:** {m['status']}")
            else:
                st.warning("No properties found within this budget currently.")
        else:
            st.info("No clients found in database.")

# --- 7. VIEW INVENTORY (EDIT/DELETE) ---
elif choice == "📋 View Inventory":
    st.title("Manage Records")
    query = st.text_input("🔍 Search Area, Owner, or Type").lower()
    
    inv_data = supabase.table("inventory").select("*").execute().data
    
    if inv_data:
        for i in inv_data:
            if query in i['area'].lower() or query in i['owner_name'].lower() or query in i['property_type'].lower():
                with st.expander(f"📍 {i['area']} | {i['property_type']} | {i['price']:,} PKR"):
                    col_a, col_b = st.columns(2)
                    col_a.write(f"**Owner:** {i['owner_name']} ({i['owner_contact']})")
                    col_a.write(f"**Specs:** {i['beds']} Beds, {i['marla']} Marla")
                    col_b.write(f"**Status:** {i['status']}")
                    
                    # Update Logic (Simplified for Streamlit)
                    new_status = col_b.selectbox("Change Status", ["Available", "Sold", "Rented"], key=f"stat_{i['id']}")
                    if col_b.button("Update Status", key=f"btn_{i['id']}"):
                        supabase.table("inventory").update({"status": new_status}).eq("id", i['id']).execute()
                        st.rerun()

                    if st.button("🗑️ Delete Property", key=f"del_{i['id']}"):
                        supabase.table("inventory").delete().eq("id", i['id']).execute()
                        st.rerun()
