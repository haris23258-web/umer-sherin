import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote

# --- CONFIGURATION ---
st.set_page_config(page_title="Twin Cities Realty ERP Pro", layout="wide")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- DB CONNECTION ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Database Connection Failed!")
    st.stop()

# --- AUTH SYSTEM ---
USERS = {
    "sawer khan": {"pwd": "sawer123", "role": "Manager"},
    "tariq": {"pwd": "tariq456", "role": "Manager"},
    "agent1": {"pwd": "pindi786", "role": "Agent"}
}

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Enterprise Portal Login")
    with st.container(border=True):
        u = st.text_input("Username").lower().strip()
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            if u in USERS and USERS[u]['pwd'] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.session_state.role = USERS[u]['role']
                st.rerun()
            else: st.error("Access Denied!")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🏢 Realty ERP v4.0")
st.sidebar.write(f"Welcome: **{st.session_state.user.title()}**")
nav = st.sidebar.radio("MAIN MODULES", [
    "📊 Executive Dashboard", 
    "🏠 Property Inventory", 
    "👥 Client CRM & Matching", 
    "💰 Accounts & Expenses"
])
if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()

# --- 1. DASHBOARD ---
if nav == "📊 Executive Dashboard":
    st.title("Performance Analytics")
    inv = supabase.table("inventory").select("*").execute().data
    cli = supabase.table("clients").select("*").execute().data
    acc = supabase.table("accounts").select("*").execute().data
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Listings", len(inv) if inv else 0)
    m2.metric("Active Leads", len(cli) if cli else 0)
    
    if acc:
        df_acc = pd.DataFrame(acc)
        inc = df_acc[df_acc['type']=='Income']['amount'].sum()
        exp = df_acc[df_acc['type']=='Expense']['amount'].sum()
        m3.metric("Monthly Income", f"{inc:,}")
        m4.metric("Net Profit", f"{inc-exp:,}")

    st.divider()
    if inv:
        st.subheader("📍 Inventory Distribution")
        st.bar_chart(pd.DataFrame(inv)['area'].value_counts())

# --- 2. PROPERTY INVENTORY ---
elif nav == "🏠 Property Inventory":
    st.title("Inventory Engine")
    t1, t2 = st.tabs(["➕ Add New", "📂 View All"])
    
    with t1:
        with st.form("inv_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            cat = c1.selectbox("Category", ["Residential", "Commercial", "Plot"])
            typ = c2.selectbox("Type", ["Sale", "Rent"])
            area = c3.text_input("Area (Sector/Phase)")
            
            c4, c5, c6 = st.columns(3)
            price = c4.number_input("Demand (PKR)", min_value=0)
            beds = c5.number_input("Beds", 0, 10)
            marla = c6.number_input("Size (Marla)", 0.0)
            
            maps = st.text_input("Google Maps Link")
            owner = st.text_input("Owner Details (Name/Contact)")
            
            if st.form_submit_button("Publish Listing"):
                supabase.table("inventory").insert({
                    "property_category": cat, "property_type": typ, "area": area,
                    "price": price, "beds": beds, "marla": marla, 
                    "location_link": maps, "owner_name": owner, "added_by": st.session_state.user
                }).execute()
                st.success("Property Added!")

    with t2:
        res = supabase.table("inventory").select("*").execute().data
        if res:
            df_v = pd.DataFrame(res)
            st.dataframe(df_v[['area', 'price', 'property_type', 'owner_name']], use_container_width=True)
            for p in res:
                with st.expander(f"🏠 {p['area']} - {p['price']:,} PKR"):
                    st.write(f"Type: {p['sub_type']} | Size: {p['marla']} Marla")
                    if p.get('location_link'): st.link_button("📍 Open Map", p['location_link'])
                    if st.button("Delete", key=f"del_{p['id']}"):
                        supabase.table("inventory").delete().eq("id", p['id']).execute()
                        st.rerun()

# --- 3. CLIENT CRM & SMART MATCH ---
elif nav == "👥 Client CRM & Matching":
    st.title("Lead Management")
    t1, t2 = st.tabs(["🆕 Add Client", "🎯 Match Engine"])
    
    with t1:
        with st.form("cli_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Client Name")
            phone = col2.text_input("Phone (e.g. 923001234567)")
            budget = st.number_input("Max Budget", min_value=0)
            req = st.selectbox("Req Type", ["Rent", "Sale"])
            if st.form_submit_button("Save Client"):
                supabase.table("clients").insert({
                    "client_name": name, "client_contact": phone, 
                    "max_budget": budget, "demand_type": req
                }).execute()
                st.success("Client Added!")

    with t2:
        cls = supabase.table("clients").select("*").execute().data
        if cls:
            sel_c = st.selectbox("Select Client", [x['client_name'] for x in cls])
            c_det = next(x for x in cls if x['client_name'] == sel_c)
            
            # Match Logic
            matches = supabase.table("inventory").select("*").eq("property_type", c_det['demand_type']).lte("price", c_det['max_budget']).execute().data
            
            if matches:
                for m in matches:
                    with st.container(border=True):
                        st.write(f"**Match Found:** {m['area']} ({m['price']:,} PKR)")
                        msg = f"Salam {c_det['client_name']}, hamare pas {m['area']} mein {m['price']:,} ki property hai. Specs: {m['beds']} beds."
                        wa_url = f"https://wa.me/{c_det['client_contact']}?text={quote(msg)}"
                        st.link_button("💬 Share on WhatsApp", wa_url)

# --- 4. ACCOUNTS ---
elif nav == "💰 Accounts & Expenses":
    st.title("Financial Ledger")
    if st.session_state.role != "Manager":
        st.error("Access Restricted to Managers only.")
    else:
        with st.form("acc_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            a_cat = c1.selectbox("Category", ["Commission", "Tea/Food", "Petrol", "Marketing", "Rent"])
            a_typ = c2.selectbox("Type", ["Income", "Expense"])
            a_amt = c3.number_input("Amount", min_value=0)
            a_desc = st.text_input("Description")
            if st.form_submit_button("Add Record"):
                supabase.table("accounts").insert({"category": a_cat, "type": a_typ, "amount": a_amt, "description": a_desc}).execute()
                st.rerun()
