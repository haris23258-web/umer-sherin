import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote

# --- 1. CONFIG & DATABASE ---
st.set_page_config(page_title="RealtyPro Enterprise", layout="wide", page_icon="🏢")

try:
    # Make sure these are in your Streamlit Secrets
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error("Database Connection Error. Please check your Supabase Secrets.")
    st.stop()

# --- 2. ADVANCED AUTH SYSTEM ---
# Admin can manage accounts, Agents can only manage properties/clients
USERS = {
    "sawer khan": {"pwd": "sawer123", "role": "Admin"},
    "tariq": {"pwd": "tariq456", "role": "Admin"},
    "agent1": {"pwd": "pindi786", "role": "Agent"}
}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 RealtyPro ERP Login")
    col_l, col_r = st.columns([1, 1])
    with col_l:
        u = st.text_input("Username").lower().strip()
        p = st.text_input("Password", type="password")
        if st.button("Login to System", use_container_width=True):
            if u in USERS and USERS[u]['pwd'] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.role = USERS[u]['role']
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    st.stop()

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title(f"Welcome, {st.session_state.user.title()}")
st.sidebar.markdown(f"**Role:** `{st.session_state.role}`")
st.sidebar.divider()

menu = st.sidebar.radio("MANAGEMENT MODULES", [
    "📊 Business Overview", 
    "🏠 Inventory Engine", 
    "👥 Client CRM", 
    "🎯 Smart Matcher", 
    "💰 Financial Ledger"
])

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()

# --- 4. MODULE: DASHBOARD ---
if menu == "📊 Business Overview":
    st.title("Market Analytics & Stats")
    
    # Fetch Data
    inv = supabase.table("inventory").select("*").execute().data
    cli = supabase.table("clients").select("*").execute().data
    acc = supabase.table("accounts").select("*").execute().data
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Listings", len(inv) if inv else 0)
    m2.metric("Total Leads", len(cli) if cli else 0)
    
    if st.session_state.role == "Admin" and acc:
        df_acc = pd.DataFrame(acc)
        total_income = df_acc[df_acc['type'] == 'Income']['amount'].sum()
        total_expense = df_acc[df_acc['type'] == 'Expense']['amount'].sum()
        m3.metric("Revenue (PKR)", f"{total_income:,}")
        m4.metric("Net Profit", f"{total_income - total_expense:,}")

    st.divider()
    if inv:
        st.subheader("Area-wise Property Distribution")
        df_inv = pd.DataFrame(inv)
        st.bar_chart(df_inv['area'].value_counts())

# --- 5. MODULE: INVENTORY ENGINE ---
elif menu == "🏠 Inventory Engine":
    st.title("Property Management")
    tab1, tab2 = st.tabs(["➕ Add New Listing", "📂 Browse Inventory"])
    
    with tab1:
        with st.form("inventory_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            category = c1.selectbox("Category", ["Residential", "Commercial", "Plot"])
            deal_type = c2.selectbox("Deal Type", ["Sale", "Rent"])
            sub_type = c3.selectbox("Sub-Type", ["House", "Flat", "Shop", "Office", "Plot"])
            
            p1, p2, p3 = st.columns(3)
            area = p1.text_input("Area / Sector")
            price = p2.number_input("Demand (PKR)", min_value=0)
            size = p3.number_input("Size (Marla/Kanal)", min_value=0.0)
            
            o1, o2 = st.columns(2)
            owner = o1.text_input("Owner Name")
            contact = o2.text_input("Owner Contact")
            maps = st.text_input("Google Maps Link")
            
            if st.form_submit_button("🚀 PUBLISH PROPERTY"):
                supabase.table("inventory").insert({
                    "property_category": category, "property_type": deal_type, "sub_type": sub_type,
                    "area": area, "price": price, "marla": size, "owner_name": owner,
                    "owner_contact": contact, "location_link": maps, "added_by": st.session_state.user
                }).execute()
                st.success("Property added to live database!")

    with tab2:
        search = st.text_input("🔍 Search Properties (Area, Type, Owner)")
        data = supabase.table("inventory").select("*").execute().data
        if data:
            for p in data:
                if not search or search.lower() in str(p).lower():
                    with st.container(border=True):
                        col_text, col_btn = st.columns([4, 1])
                        col_text.subheader(f"{p['area']} - {p['price']:,} PKR")
                        col_text.write(f"**{p['property_type']}** | {p['marla']} Marla {p['sub_type']} | Owner: {p['owner_name']}")
                        if p['location_link']: col_text.link_button("📍 Location", p['location_link'])
                        
                        if col_btn.button("🗑️ Delete", key=f"del_{p['id']}"):
                            supabase.table("inventory").delete().eq("id", p['id']).execute()
                            st.rerun()

# --- 6. MODULE: CLIENT CRM ---
elif menu == "👥 Client CRM":
    st.title("Lead Management")
    with st.form("client_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        c_name = c1.text_input("Client Name")
        c_phone = c2.text_input("WhatsApp (e.g. 923001234567)")
        
        c3, c4, c5 = st.columns(3)
        c_budget = c3.number_input("Max Budget", min_value=0)
        c_req = c4.selectbox("Requirement", ["Sale", "Rent"])
        c_status = c5.selectbox("Priority", ["Hot 🔥", "Warm", "Cold"])
        
        if st.form_submit_button("Add to Pipeline"):
            supabase.table("clients").insert({
                "client_name": c_name, "client_contact": c_phone, 
                "max_budget": c_budget, "demand_type": c_req, "status": c_status
            }).execute()
            st.success("Client registered successfully!")

# --- 7. MODULE: SMART MATCHER ---
elif menu == "🎯 Smart Matcher":
    st.title("AI-Powered Deal Matcher")
    clients = supabase.table("clients").select("*").execute().data
    if clients:
        target_client = st.selectbox("Select a Client to Match", [x['client_name'] for x in clients])
        c = next(item for item in clients if item['client_name'] == target_client)
        
        st.info(f"Targeting: {c['demand_type']} options within {c['max_budget']:,} PKR")
        
        # Logic: Match by type and budget
        matches = supabase.table("inventory").select("*").eq("property_type", c['demand_type']).lte("price", c['max_budget']).execute().data
        
        if matches:
            st.success(f"Found {len(matches)} matches for {target_client}!")
            for m in matches:
                with st.container(border=True):
                    st.write(f"🏠 **{m['area']}** - {m['price']:,} PKR ({m['marla']} Marla)")
                    msg = f"Salam {c['client_name']}, hamare paas {m['area']} mein aik zabardast option hai aapke budget ke mutabiq. Price: {m['price']:,} PKR."
                    wa_url = f"https://wa.me/{c['client_contact']}?text={quote(msg)}"
                    st.link_button("💬 Share Details via WhatsApp", wa_url)
        else:
            st.warning("No properties matching this client's criteria.")

# --- 8. MODULE: FINANCIAL LEDGER ---
elif menu == "💰 Financial Ledger":
    st.title("Accounts & Commissions")
    if st.session_state.role != "Admin":
        st.error("Access Restricted! Sirf Admin accounts dekh sakta hai.")
    else:
        with st.form("acc_form", clear_on_submit=True):
            a1, a2, a3 = st.columns(3)
            a_type = a1.selectbox("Type", ["Income", "Expense"])
            a_cat = a2.selectbox("Category", ["Commission", "Marketing", "Office Rent", "Salaries", "Misc"])
            a_amt = a3.number_input("Amount (PKR)", min_value=0)
            a_desc = st.text_input("Description / Deal Details")
            if st.form_submit_button("Save Transaction"):
                supabase.table("accounts").insert({"type": a_type, "category": a_cat, "amount": a_amt, "description": a_desc}).execute()
                st.success("Account Ledger Updated!")
