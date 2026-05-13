import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote
import plotly.express as px  # Professional Charts ke liye

# --- 1. CONNECTION & PAGE SETUP ---
st.set_page_config(page_title="Twin Cities Realty Pro", layout="wide", page_icon="🏢")

try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Database Connection Failed!")
    st.stop()

# --- 2. AUTH SYSTEM ---
ADMINS = {"sawer khan": "sawer123", "tariq": "tariq456"}
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Realty Pro ERP Login")
    with st.container(border=True):
        u = st.text_input("Username").lower().strip()
        p = st.text_input("Password", type="password")
        if st.button("Access System", use_container_width=True):
            if u in ADMINS and ADMINS[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Invalid Credentials.")
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=80)
    st.title("Admin Portal")
    st.write(f"Logged in: **{st.session_state.user.title()}**")
    st.divider()
    menu = st.radio("MAIN MODULES", [
        "📊 Dashboard & Analytics", 
        "🏠 Inventory Manager", 
        "👥 Client CRM", 
        "🎯 Smart Match Engine",
        "💰 Accounts Ledger"
    ])
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

# --- 4. DASHBOARD & ANALYTICS ---
if menu == "📊 Dashboard & Analytics":
    st.title("Business Intelligence Dashboard")
    inv = supabase.table("inventory").select("*").execute().data
    cli = supabase.table("clients").select("*").execute().data
    acc = supabase.table("accounts").select("*").execute().data
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Live Inventory", len(inv) if inv else 0)
    col2.metric("Total Clients", len(cli) if cli else 0)
    
    if acc:
        df_acc = pd.DataFrame(acc)
        inc = df_acc[df_acc['type']=='Income']['amount'].sum()
        exp = df_acc[df_acc['type']=='Expense']['amount'].sum()
        col3.metric("Total Revenue", f"{inc:,}")
        col4.metric("Net Profit", f"{inc-exp:,}")

    st.divider()
    
    if inv:
        df_inv = pd.DataFrame(inv)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Inventory by Area")
            fig = px.pie(df_inv, names='area', hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Price Trends")
            fig2 = px.histogram(df_inv, x='price', nbins=10, color_discrete_sequence=['#007bff'])
            st.plotly_chart(fig2, use_container_width=True)

# --- 5. INVENTORY MANAGER ---
elif menu == "🏠 Inventory Manager":
    st.title("Property Inventory Engine")
    t1, t2 = st.tabs(["➕ Add New Listing", "📂 Global Search"])
    
    with t1:
        with st.form("inv_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            cat = col1.selectbox("Category", ["Residential", "Commercial", "Plot"])
            dtype = col2.selectbox("Deal", ["Sale", "Rent"])
            area = col3.text_input("Area / Sector")
            
            p1, p2, p3 = st.columns(3)
            price = p1.number_input("Demand (PKR)", min_value=0)
            beds = p2.number_input("Beds", 0, 15)
            marla = p3.number_input("Size (Marla)", 0.1)
            
            owner = st.text_input("Owner Name & Contact")
            maps = st.text_input("Google Maps Link")
            
            if st.form_submit_button("🚀 Publish to Inventory"):
                supabase.table("inventory").insert({
                    "property_category": cat, "property_type": dtype, "area": area,
                    "price": price, "beds": beds, "marla": marla, "owner_name": owner,
                    "location_link": maps, "added_by": st.session_state.user
                }).execute()
                st.success("Listing is live!")

    with t2:
        search = st.text_input("🔍 Quick Search by Area or Owner")
        data = supabase.table("inventory").select("*").execute().data
        if data:
            df = pd.DataFrame(data)
            if search:
                df = df[df['area'].str.contains(search, case=False) | df['owner_name'].str.contains(search, case=False)]
            st.dataframe(df[['area', 'price', 'property_type', 'owner_name']], use_container_width=True)

# --- 6. CLIENT CRM ---
elif menu == "👥 Client CRM":
    st.title("Client Relationship Management")
    with st.form("client_reg"):
        c1, c2 = st.columns(2)
        cname = c1.text_input("Client Name")
        cphone = c2.text_input("WhatsApp (e.g. 923001234567)")
        
        c3, c4, c5 = st.columns(3)
        cbudget = c3.number_input("Max Budget (PKR)", min_value=0)
        ctype = c4.selectbox("Interested In", ["Rent", "Sale"])
        cstatus = c5.selectbox("Lead Priority", ["Hot 🔥", "Warm ⚡", "Cold ❄️"])
        
        if st.form_submit_button("Register Lead"):
            supabase.table("clients").insert({
                "client_name": cname, "client_contact": cphone, 
                "max_budget": cbudget, "demand_type": ctype, "status": cstatus
            }).execute()
            st.success("Lead Saved!")

# --- 7. SMART MATCH ENGINE (Advanced) ---
elif menu == "🎯 Smart Match Engine":
    st.title("AI Smart Matcher")
    clients = supabase.table("clients").select("*").execute().data
    if clients:
        sel_client = st.selectbox("Select Client to Find Matches", [x['client_name'] for x in clients])
        c = next(x for x in clients if x['client_name'] == sel_client)
        
        st.info(f"Target: {c['demand_type']} up to {c['max_budget']:,} PKR")
        
        # Advanced Filtering Logic
        matches = supabase.table("inventory").select("*")\
            .eq("property_type", c['demand_type'])\
            .lte("price", c['max_budget'])\
            .execute().data
        
        if matches:
            for m in matches:
                with st.container(border=True):
                    col_m1, col_m2 = st.columns([3, 1])
                    with col_m1:
                        st.subheader(f"🏠 {m['area']} - {m['price']:,} PKR")
                        st.write(f"Type: {m['property_category']} | Size: {m['marla']} Marla")
                    with col_m2:
                        msg = f"Salam {c['client_name']}, hamare paas {m['area']} mein aap ke liye option hai. Price: {m['price']:,} PKR."
                        st.link_button("💬 WhatsApp Share", f"https://wa.me/{c['client_contact']}?text={quote(msg)}")
        else:
            st.warning("No matches found in inventory.")

# --- 8. ACCOUNTS LEDGER ---
elif menu == "💰 Accounts Ledger":
    st.title("Financial Records")
    with st.expander("Record New Transaction"):
        with st.form("acc_entry"):
            a1, a2, a3 = st.columns(3)
            atyp = a1.selectbox("Type", ["Income", "Expense"])
            acat = a2.selectbox("Category", ["Commission", "Marketing", "Tea/Expenses", "Fuel", "Rent"])
            aamt = a3.number_input("Amount (PKR)", min_value=0)
            adesc = st.text_input("Description")
            if st.form_submit_button("Save Entry"):
                supabase.table("accounts").insert({"type": atyp, "category": acat, "amount": aamt, "description": adesc}).execute()
                st.rerun()
