import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote # For WhatsApp message encoding

# --- UI SETTINGS ---
st.set_page_config(page_title="Pindi-Isloo Realty CRM Pro", layout="wide", page_icon="📈")

# Custom Styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; color: #007bff; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8f9fa; border-radius: 5px; padding: 10px; }
    .stTabs [aria-selected="true"] { background-color: #007bff !important; color: white !important; }
    div[data-testid="stExpander"] { border: 1px solid #007bff; border-radius: 10px; }
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
    st.header("🏢 Estate Pro v4.0")
    st.write(f"User: **{st.session_state.user.title()}**")
    nav = st.sidebar.radio("MAIN MENU", [
        "📊 Performance Dashboard", 
        "🏠 Inventory Engine", 
        "👥 Client CRM & Matching", 
        "🔍 Advanced Search",
        "💰 Financial Ledger" # New Advance Feature
    ])
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
                    "gas": gas, "water": water, "electricity": elec, "owner_name": oname, "owner_contact": ocont,
                    "status": "Available" # Auto status
                }).execute()
                st.success("Property Added!")

    with tab_view:
        inv_all = supabase.table("inventory").select("*").order("created_at", desc=True).execute().data
        if inv_all:
            # Advance Status Update Integration
            for p in inv_all:
                with st.expander(f"📍 {p['area']} - {p['price']:,} PKR ({p['status']})"):
                    st.write(f"Owner: {p['owner_name']} | Contact: {p['owner_contact']}")
                    if st.button("Mark as SOLD", key=f"sold_{p['id']}"):
                        supabase.table("inventory").update({"status": "Sold"}).eq("id", p['id']).execute()
                        st.rerun()

# --- 3. CLIENT CRM & SMART MATCH ---
elif nav == "👥 Client CRM & Matching":
    st.title("Client Relations & Lead Matching")
    tab_c1, tab_c2 = st.tabs(["🆕 Register New Client", "🎯 Smart Matching Engine"])
    
    with tab_c1:
        with st.form("client_form", clear_on_submit=True):
            c_name = st.text_input("Client Name")
            c_cont = st.text_input("Client Phone (92300XXXXXXX)")
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
            
            st.info(f"Targeting: {cl_data['demand_type']} within {cl_data['max_budget']:,} PKR")
            
            matches = supabase.table("inventory").select("*")\
                .eq("property_type", cl_data['demand_type'])\
                .lte("price", cl_data['max_budget'])\
                .gte("price", cl_data['min_budget'])\
                .eq("status", "Available")\
                .execute().data
            
            if matches:
                for m in matches:
                    with st.container(border=True):
                        col_m1, col_m2 = st.columns([3, 1])
                        with col_m1:
                            st.subheader(f"🏠 {m['area']} - {m['price']:,} PKR")
                            st.write(f"**Specs:** {m['beds']} Beds | {m['marla']} Marla | {m['sub_type']}")
                        with col_m2:
                            # ADVANCE: WhatsApp Link Generation
                            wa_msg = f"Salam {selected_client}, hamare pas {m['area']} mein aik option hai. {m['marla']} Marla {m['sub_type']}, Demand: {m['price']:,} PKR. Contact us for visit."
                            wa_url = f"https://wa.me/{cl_data['client_contact']}?text={quote(wa_msg)}"
                            st.link_button("📲 Send to WhatsApp", wa_url)
            else:
                st.warning("No matches found.")

# --- 4. ADVANCED SEARCH ---
elif nav == "🔍 Advanced Search":
    st.title("Enterprise Filtering Engine")
    with st.container(border=True):
        f1, f2, f3 = st.columns(3)
        s_area = f1.text_input("Filter by Area")
        s_type = f2.selectbox("Filter by Type", ["All", "Rent", "Sale"])
        s_max = f3.number_input("Max Budget", value=100000000)
        
        query = supabase.table("inventory").select("*").lte("price", s_max)
        if s_type != "All": query = query.eq("property_type", s_type)
        if s_area: query = query.ilike("area", f"%{s_area}%")
        
        results = query.execute().data
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)

# --- 5. FINANCIAL LEDGER (Admin Feature) ---
elif nav == "💰 Financial Ledger":
    st.title("Office Finance Management")
    if st.session_state.user not in ["sawer khan", "tariq"]:
        st.error("Restricted Access!")
    else:
        with st.form("finance_form"):
            f_col1, f_col2 = st.columns(2)
            f_type = f_col1.selectbox("Entry Type", ["Income (Commission)", "Expense (Marketing/Rent)"])
            f_amt = f_col2.number_input("Amount (PKR)", min_value=0)
            f_desc = st.text_area("Transaction Details")
            if st.form_submit_button("Record Transaction"):
                supabase.table("accounts").insert({
                    "type": f_type, "amount": f_amt, "details": f_desc, "added_by": st.session_state.user
                }).execute()
                st.success("Ledger Updated!")
