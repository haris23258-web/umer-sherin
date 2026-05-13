import streamlit as st
from supabase import create_client
import pandas as pd

# --- UI SETTINGS ---
st.set_page_config(page_title="Pindi-Isloo Realty CRM Pro", layout="wide", page_icon="📈")

# Custom Styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; color: #007bff; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8f9fa; border-radius: 5px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #007bff !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- DB CONNECTION ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Database Connection Error!")
    st.stop()

# --- AUTHENTICATION ---
ADMINS = {"sawer khan": "sawer123", "tariq": "tariq456", "admin3": "pindi786"}
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Enterprise Portal Login")
    with st.container(border=True):
        u = st.text_input("Username").lower().strip()
        p = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if u in ADMINS and ADMINS[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.header("🏢 Estate Pro v3.0")
    st.write(f"User: **{st.session_state.user.title()}**")
    nav = st.radio("MAIN MENU", ["📊 Performance Dashboard", "🏠 Inventory Engine", "👥 Client CRM & Matching", "🔍 Advanced Search"])
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

# --- 1. DASHBOARD ---
if nav == "📊 Performance Dashboard":
    st.title("Market Analytics Dashboard")
    inv = supabase.table("inventory").select("*").execute().data
    cli = supabase.table("clients").select("*").execute().data
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Inventory", len(inv) if inv else 0)
    c2.metric("Total Clients", len(cli) if cli else 0)
    c3.metric("Available for Rent", len([x for x in inv if x['property_type']=='Rent']) if inv else 0)
    c4.metric("Available for Sale", len([x for x in inv if x['property_type']=='Sale']) if inv else 0)
    
    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📍 Hot Locations")
        if inv:
            df = pd.DataFrame(inv)
            st.bar_chart(df['area'].value_counts())
    with col_r:
        st.subheader("📋 Recent Lead Pipeline")
        if cli:
            df_c = pd.DataFrame(cli)
            st.dataframe(df_c[['client_name', 'demand_type', 'max_budget']].tail(5), use_container_width=True)

# --- 2. INVENTORY ENGINE ---
elif nav == "🏠 Inventory Engine":
    st.title("Property Management")
    tab_add, tab_view = st.tabs(["➕ Add New Listing", "📂 All Inventory"])
    
    with tab_add:
        with st.form("inv_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            cat = col1.selectbox("Category", ["Residential", "Commercial", "Plot"])
            dtype = col2.selectbox("Type", ["Rent", "Sale"])
            sub = col3.selectbox("Sub-type", ["House", "Flat", "Shop", "Office", "Plot", "Warehouse"])
            
            area = st.text_input("Area / Sector (e.g. DHA Phase 4, Bahria Phase 7, G-11)")
            
            c4, c5, c6 = st.columns(3)
            price = c4.number_input("Demand (PKR)", min_value=0)
            beds = c5.number_input("Beds", 0, 15)
            marla = c6.number_input("Size (Marla)", 0.1)
            
            st.subheader("⚡ Utilities")
            u1, u2, u3 = st.columns(3)
            gas = u1.selectbox("Gas", ["Yes", "No", "Shared"])
            water = u2.selectbox("Water", ["Supply", "Boring", "Tanker"])
            elec = u3.selectbox("Electricity", ["Separate", "Shared", "Solar"])
            
            oname = st.text_input("Owner Name")
            ocont = st.text_input("Owner Contact")
            
            if st.form_submit_button("Publish Property"):
                supabase.table("inventory").insert({
                    "added_by": st.session_state.user, "property_category": cat, "property_type": dtype,
                    "sub_type": sub, "area": area, "price": price, "beds": beds, "marla": marla,
                    "gas": gas, "water": water, "electricity": elec, "owner_name": oname, "owner_contact": ocont
                }).execute()
                st.success("Property Added!")

    with tab_view:
        inv_all = supabase.table("inventory").select("*").order("created_at", desc=True).execute().data
        if inv_all:
            st.dataframe(pd.DataFrame(inv_all), use_container_width=True)

# --- 3. CLIENT CRM & SMART MATCH ---
elif nav == "👥 Client CRM & Matching":
    st.title("Client Relations & Lead Matching")
    tab_c1, tab_c2 = st.tabs(["🆕 Register New Client", "🎯 Smart Matching Engine"])
    
    with tab_c1:
        with st.form("client_form", clear_on_submit=True):
            c_name = st.text_input("Client Name")
            c_cont = st.text_input("Client Phone")
            c_type = st.selectbox("Looking for", ["Rent", "Sale"])
            c_min = st.number_input("Min Budget (PKR)", 0)
            c_max = st.number_input("Max Budget (PKR)", 0)
            c_area = st.text_input("Preferred Area")
            c_beds = st.number_input("Min Beds Required", 0)
            
            if st.form_submit_button("Add to Pipeline"):
                supabase.table("clients").insert({
                    "client_name": c_name, "client_contact": c_cont, "demand_type": c_type,
                    "min_budget": c_min, "max_budget": c_max, "preferred_area": c_area, "min_beds": c_beds
                }).execute()
                st.success("Client Requirement Saved!")

    with tab_c2:
        clients = supabase.table("clients").select("*").execute().data
        if clients:
            selected_client = st.selectbox("Select Client to Match", [x['client_name'] for x in clients])
            cl_data = next(x for x in clients if x['client_name'] == selected_client)
            
            st.info(f"Finding properties for {selected_client} (Budget: {cl_data['max_budget']:,} PKR)")
            
            # Match Logic
            matches = supabase.table("inventory").select("*")\
                .eq("property_type", cl_data['demand_type'])\
                .lte("price", cl_data['max_budget'])\
                .gte("price", cl_data['min_budget'])\
                .execute().data
            
            if matches:
                for m in matches:
                    with st.container(border=True):
                        col_m1, col_m2 = st.columns([3, 1])
                        with col_m1:
                            st.subheader(f"🏠 {m['area']} - {m['price']:,} PKR")
                            st.write(f"**Specs:** {m['beds']} Beds | {m['marla']} Marla | {m['sub_type']}")
                            st.write(f"**Utilities:** Gas: {m['gas']} | Water: {m['water']}")
                        with col_m2:
                            st.write("**Owner Info**")
                            st.write(m['owner_name'])
                            st.write(m['owner_contact'])
            else:
                st.warning("No matches found in inventory for this client yet.")
