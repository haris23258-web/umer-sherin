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
st.set_page_config(page_title="Pindi-Isloo Real Estate ERP", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏢 Estate Manager v1.0")
menu = ["📊 Dashboard", "🏠 Add Property", "👥 Client Desk & Match", "📋 View Inventory"]
choice = st.sidebar.radio("Navigate", menu)

# --- 4. DASHBOARD LOGIC ---
if choice == "📊 Dashboard":
    st.title("Main Dashboard")
    
    # Fetching counts
    inv_count = supabase.table("inventory").select("*", count="exact").execute()
    cli_count = supabase.table("clients").select("*", count="exact").execute()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Properties", inv_count.count if inv_count.count else 0)
    col2.metric("Active Clients", cli_count.count if cli_count.count else 0)
    col3.metric("Office Status", "Online")
    
    st.divider()
    st.subheader("Quick Actions")
    st.info("Pindi aur Islamabad ke office staff ke liye tayyar karda professional system.")

# --- 5. ADD PROPERTY (INVENTORY) ---
elif choice == "🏠 Add Property":
    st.title("Register New Property")
    with st.form("property_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        p_type = c1.selectbox("Type", ["Rent", "Sale"])
        area = c2.text_input("Area (e.g. F-11, DHA 7, Bahria)")
        
        c3, c4, c5 = st.columns(3)
        price = c3.number_input("Price (PKR)", min_value=0)
        beds = c4.number_input("Beds", min_value=1, max_value=12)
        marla = c5.number_input("Marla Size", min_value=1.0)
        
        portion = st.selectbox("Portion", ["Full House", "Ground Floor", "First Floor", "Basement", "Plot"])
        
        st.subheader("Utilities")
        u1, u2, u3 = st.columns(3)
        gas = u1.checkbox("Gas")
        elec = u2.checkbox("Electricity")
        water = u3.checkbox("Water")
        
        st.subheader("Owner Details (Private)")
        o_name = st.text_input("Owner Name")
        o_phone = st.text_input("Owner Contact Number")
        
        if st.form_submit_button("Save to Inventory"):
            data = {
                "property_type": p_type, "area": area, "price": price, 
                "beds": beds, "marla": marla, "portion": portion,
                "owner_name": o_name, "owner_contact": o_phone,
                "status": "Available"
            }
            supabase.table("inventory").insert(data).execute()
            st.success(f"Property in {area} saved successfully!")

# --- 6. CLIENT DESK & SMART MATCH ---
elif choice == "👥 Client Desk & Match":
    st.title("Client Requirements & Smart Match")
    
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
        clients = supabase.table("clients").select("*").execute().data
        if clients:
            target = st.selectbox("Select Client", [c['client_name'] for c in clients])
            c_data = next(x for x in clients if x['client_name'] == target)
            
            # Logic: Match type and Price <= Budget
            matches = supabase.table("inventory").select("*")\
                .eq("property_type", c_data['requirement_type'])\
                .lte("price", c_data['budget_max'])\
                .execute().data
            
            if matches:
                st.write(f"Found {len(matches)} matches for {target}:")
                for m in matches:
                    with st.expander(f"🏠 {m['area']} - {m['price']} PKR"):
                        st.write(f"Owner Contact: {m['owner_contact']}")
                        st.write(f"Beds: {m['beds']} | Size: {m['marla']} Marla")
            else:
                st.warning("No matches found within this budget.")

# --- 7. VIEW INVENTORY (EDIT/DELETE) ---
elif choice == "📋 View Inventory":
    st.title("Manage Office Records")
    
    # Search filter
    query = st.text_input("🔍 Search by Area or Owner Name").lower()
    
    inv_data = supabase.table("inventory").select("*").execute().data
    
    if inv_data:
        for i in inv_data:
            # Filter logic
            if query in i['area'].lower() or query in i['owner_name'].lower():
                with st.expander(f"📍 {i['area']} | {i['property_type']} | {i['price']} PKR"):
                    st.write(f"**Owner:** {i['owner_name']} ({i['owner_contact']})")
                    st.write(f"**Specs:** {i['beds']} Beds, {i['marla']} Marla, {i['portion']}")
                    st.write(f"**Current Status:** {i['status']}")
                    
                    c_ed, c_del = st.columns(2)
                    
                    # Delete Logic
                    if c_del.button("🗑️ Delete Property", key=f"del_{i['id']}"):
                        supabase.table("inventory").delete().eq("id", i['id']).execute()
                        st.warning("Record deleted.")
                        st.rerun()
                    
                    # Edit Logic
                    if c_ed.button("✏️ Change Status", key=f"ed_{i['id']}"):
                        new_stat = st.selectbox("Mark as:", ["Available", "Sold", "Rented"], key=f"sel_{i['id']}")
                        if st.button("Confirm Update", key=f"upd_{i['id']}"):
                            supabase.table("supabase").update({"status": new_stat}).eq("id", i['id']).execute()
                            st.success("Status Updated!")
                            st.rerun()
