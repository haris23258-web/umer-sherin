import streamlit as st
from supabase import create_client
import pandas as pd

# --- 1. DATABASE CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Secrets configuration missing!")
    st.stop()

# --- 2. AUTHENTICATION ---
ADMIN_USERS = {
    "sawer khan": "sawer123",
    "tariq": "tariq456",
    "admin3": "pindi786"
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Office Login")
    with st.form("login_form"):
        user = st.text_input("Username").lower().strip()
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user in ADMIN_USERS and ADMIN_USERS[user] == pwd:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Ghalat Password!")
    st.stop()

# --- 3. UI CONFIG ---
st.set_page_config(page_title="Estate Manager Pro", layout="wide")
st.sidebar.title(f"👤 {st.session_state['user'].title()}")
choice = st.sidebar.radio("Navigate", ["📊 Dashboard", "🏠 Add Property", "👥 Client Desk", "📋 View Inventory"])

if st.sidebar.button("Log Out"):
    st.session_state["authenticated"] = False
    st.rerun()

# --- 4. DASHBOARD ---
if choice == "📊 Dashboard":
    st.title("📈 Reporting Dashboard")
    # Yahan dashboard ki logic purani wali hi rahegi
    st.info("Pindi-Isloo Office ki mukammal report yahan dekhein.")

# --- 5. ADD PROPERTY (Updated with Gas/Water/Bijli) ---
elif choice == "🏠 Add Property":
    st.title("Register New Property")
    with st.form("property_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        p_type = col1.selectbox("Type", ["Rent", "Sale"])
        area = col2.text_input("Area (e.g. DHA, Bahria, Gulberg)")
        
        c3, c4, c5 = st.columns(3)
        price = c3.number_input("Price (PKR)", min_value=0)
        beds = c4.number_input("Beds", min_value=0)
        marla = c5.number_input("Marla Size", min_value=1.0)

        st.subheader("⚡ Utilities & Facilities")
        u1, u2, u3 = st.columns(3)
        
        # Gas Details
        gas = u1.selectbox("Gas Status", ["No Gas", "Available (Separate)", "Available (Combined)"])
        
        # Water Details
        water = u2.selectbox("Water Source", ["Boring", "Water Supply", "Tanker Only", "Supply + Boring"])
        
        # Electricity Details
        elec = u3.selectbox("Electricity", ["Separate Meter", "Combined Meter", "Solar Installed"])

        st.subheader("Owner Details")
        o_name = st.text_input("Owner Name")
        o_phone = st.text_input("Owner Contact")
        
        if st.form_submit_button("Save Property"):
            data = {
                "property_type": p_type, "area": area, "price": price,
                "beds": beds, "marla": marla, "gas": gas, "water": water,
                "electricity": elec, "owner_name": o_name, 
                "owner_contact": o_phone, "status": "Available",
                "added_by": st.session_state["user"]
            }
            supabase.table("inventory").insert(data).execute()
            st.success("Property with complete utilities saved!")

# --- 6. VIEW INVENTORY (Detailed Display) ---
elif choice == "📋 View Inventory":
    st.title("Office Inventory")
    inv_data = supabase.table("inventory").select("*").execute().data
    
    if inv_data:
        for i in inv_data:
            with st.expander(f"📍 {i['area']} - {i['price']:,} PKR"):
                st.write(f"**Status:** {i['status']} | **Added By:** {i.get('added_by', 'N/A')}")
                st.write(f"**Specs:** {i['beds']} Beds | {i['marla']} Marla")
                
                # Utilities Display
                st.write("---")
                st.markdown(f"🔥 **Gas:** {i.get('gas', 'N/A')} | 💧 **Water:** {i.get('water', 'N/A')} | ⚡ **Elec:** {i.get('electricity', 'N/A')}")
                st.write("---")
                
                st.write(f"**Owner:** {i['owner_name']} ({i['owner_contact']})")
                
                if st.button("Delete", key=f"del_{i['id']}"):
                    supabase.table("inventory").delete().eq("id", i['id']).execute()
                    st.rerun()
