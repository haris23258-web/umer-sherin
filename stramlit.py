import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. DATABASE CONNECTION ---
# Streamlit secrets se connection details uthana
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
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; background-color: #007bff; color: white; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 Estate Manager v1.2")
st.sidebar.info("Authorized Personnel Only")
menu = ["📊 Dashboard", "🏠 Add Property", "👥 Client Desk & Match", "📋 View Inventory"]
choice = st.sidebar.radio("Navigate", menu)

# --- 4. DASHBOARD LOGIC ---
if choice == "📊 Dashboard":
    st.title("Main Dashboard")
    
    # Fetching counts with error handling
    try:
        inv_count = supabase.table("inventory").select("*", count="exact").execute()
        cli_count = supabase.table("clients").select("*", count="exact").execute()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Properties", inv_count.count if inv_count.count else 0)
        col2.metric("Active Clients", cli_count.count if cli_count.count else 0)
        col3.metric("Office Status", "Online 🟢")
    except Exception as e:
        st.warning("Database Tables connect nahi hain. Please check Supabase.")
    
    st.divider()
    st.subheader("Pindi-Islamabad Market Overview")
    st.info("DHA, Bahria, aur E/F Sectors ka inventory data yahan manage karein.")

# --- 5. ADD PROPERTY ---
elif choice == "🏠 Add Property":
    st.title("Register New Property")
    with st.form("property_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        p_type = c1.selectbox("Type", ["Rent", "Sale"])
        area = c2.text_input("Area (e.g. F-11, DHA 7, Bahria)")
        
        c3, c4, c5 = st.columns(3)
        price = c3.number_input("Price (PKR)", min_value=0)
        beds = c4.number_input("Beds", min_value=0, max_value=15)
        marla = c5.number_input("Marla Size", min_value=1.0)
        
        portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Plot", "Flat"])
        
        st.subheader("Owner Details (Private)")
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
                st.success(f"Property in {area} saved successfully!")
            else:
                st.error("Please fill required fields (Area & Owner Name)")

# --- 6. CLIENT DESK & SMART MATCH ---
elif choice == "👥 Client Desk & Match":
    st.title("Client Requirements")
    tab1, tab2 = st.tabs(["Add New Client", "Find Matches"])
    
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
                st.success("Client added to database.")

    with tab2:
        st.subheader("🎯 Auto-Match System")
        clients_data = supabase.table("clients").select("*").execute().data
        if clients_data:
            target = st.selectbox("Select Client", [c['client_name'] for c in clients_data])
            c_data = next(x for x in clients_data if x['client_name'] == target)
            
            matches = supabase.table("inventory").select("*")\
                .eq("property_type", c_data['requirement_type'])\
                .lte("price", c_data['budget_max'])\
                .execute().data
            
            if matches:
                st.write(f"Found {len(matches)} matches for {target}:")
                for m in matches:
                    with st.expander(f"🏠 {m['area']} - {m['price']:,} PKR"):
                        st.write(f"**Owner:** {m['owner_name']} | **Contact:** {m['owner_contact']}")
                        st.write(f"**Specs:** {m['beds']} Beds | {m['marla']} Marla")
            else:
                st.warning("No matches found within this budget.")

# --- 7. VIEW INVENTORY ---
elif choice == "📋 View Inventory":
    st.title("Manage Office Records")
    query = st.text_input("🔍 Search by Area or Owner").lower()
    
    inv_data = supabase.table("inventory").select("*").execute().data
    
    if inv_data:
        for i in inv_data:
            if query in i['area'].lower() or query in i['owner_name'].lower():
                with st.expander(f"📍 {i['area']} | {i['property_type']} | {i['price']:,} PKR"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Owner:** {i['owner_name']} ({i['owner_contact']})")
                        st.write(f"**Specs:** {i['beds']} Beds, {i['marla']} Marla")
                    with col2:
                        st.write(f"**Status:** {i['status']}")
                        # Simple Status Update
                        new_stat = st.selectbox("Change to:", ["Available", "Sold", "Rented"], key=f"s_{i['id']}")
                        if st.button("Update Status", key=f"b_{i['id']}"):
                            supabase.table("inventory").update({"status": new_stat}).eq("id", i['id']).execute()
                            st.rerun()
                    
                    if st.button("🗑️ Delete Record", key=f"d_{i['id']}"):
                        supabase.table("inventory").delete().eq("id", i['id']).execute()
                        st.rerun()
