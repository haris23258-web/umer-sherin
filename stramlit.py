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

# --- 2. AUTHENTICATION SYSTEM ---
# Admin Credentials Dictionary
ADMIN_USERS = {
    "sawer khan": "sawer123",
    "tariq": "tariq456",
    "admin3": "pindi786"
}

def login_screen():
    st.title("🔐 Office Login")
    with st.form("login_form"):
        user = st.text_input("Username").lower().strip()
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if user in ADMIN_USERS and ADMIN_USERS[user] == pwd:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Ghalat Username ya Password!")

# Session check
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_screen()
    st.stop()

# --- 3. UI CONFIGURATION ---
st.set_page_config(page_title="Estate Manager Pro", layout="wide")

# Sidebar Logout Button
if st.sidebar.button("Log Out"):
    st.session_state["authenticated"] = False
    st.rerun()

st.sidebar.title(f"👤 Admin: {st.session_state['user'].title()}")
menu = ["📊 Dashboard", "🏠 Add Property", "👥 Client Desk & Match", "📋 View Inventory"]
choice = st.sidebar.radio("Navigate", menu)

# --- 4. DASHBOARD (Sari Report) ---
if choice == "📊 Dashboard":
    st.title("📈 Central Reporting Dashboard")
    
    # Data fetch karein reports ke liye
    inv_data = supabase.table("inventory").select("*").execute().data
    cli_data = supabase.table("clients").select("*").execute().data
    
    df_inv = pd.DataFrame(inv_data)
    df_cli = pd.DataFrame(cli_data)

    # Top Row Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Properties", len(df_inv) if not df_inv.empty else 0)
    c2.metric("Total Clients", len(df_cli) if not df_cli.empty else 0)
    
    if not df_inv.empty:
        sold_count = len(df_inv[df_inv['status'].isin(['Sold', 'Rented'])])
        available_count = len(df_inv[df_inv['status'] == 'Available'])
        c3.metric("Closed Deals", sold_count)
        c4.metric("Available Now", available_count)

    st.divider()

    # Detailed Reports
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📍 Area-wise Inventory")
        if not df_inv.empty:
            area_report = df_inv['area'].value_counts()
            st.bar_chart(area_report)
        else:
            st.info("No inventory data.")

    with col_right:
        st.subheader("💰 Price Analysis")
        if not df_inv.empty:
            st.write("Average Property Prices:")
            avg_price = df_inv.groupby('property_type')['price'].mean().map('{:,.0f} PKR'.format)
            st.table(avg_price)

    st.subheader("📋 Recent Inventory Additions")
    if not df_inv.empty:
        st.dataframe(df_inv[['area', 'property_type', 'price', 'status']].tail(10), use_container_width=True)

# --- 5. ADD PROPERTY ---
elif choice == "🏠 Add Property":
    st.title("Register New Property")
    with st.form("property_entry", clear_on_submit=True):
        c1, c2 = st.columns(2)
        p_type = c1.selectbox("Type", ["Rent", "Sale"])
        area = c2.text_input("Area (e.g. DHA, Bahria, Gulberg)")
        
        c3, c4, c5 = st.columns(3)
        price = c3.number_input("Price (PKR)", min_value=0)
        beds = c4.number_input("Beds", min_value=0)
        marla = c5.number_input("Marla Size", min_value=1.0)
        
        o_name = st.text_input("Owner Name")
        o_phone = st.text_input("Owner Contact")
        
        if st.form_submit_button("Save Property"):
            supabase.table("inventory").insert({
                "property_type": p_type, "area": area, "price": price,
                "beds": beds, "marla": marla, "owner_name": o_name, 
                "owner_contact": o_phone, "status": "Available",
                "added_by": st.session_state["user"] # Track kisne add kiya
            }).execute()
            st.success("Property Saved!")

# --- 6. CLIENT DESK ---
elif choice == "👥 Client Desk & Match":
    st.title("Client Requirements")
    # (Pichla wala logic yahan copy-paste hoga)
    st.info("Yahan se clients aur matches manage karein.")

# --- 7. VIEW INVENTORY ---
elif choice == "📋 View Inventory":
    st.title("Office Inventory")
    inv_data = supabase.table("inventory").select("*").execute().data
    if inv_data:
        df = pd.DataFrame(inv_data)
        st.dataframe(df)
