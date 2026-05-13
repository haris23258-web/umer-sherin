import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote

# --- 1. DB CONNECTION ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Database Connection Failed!")
    st.stop()

# --- 2. AUTHENTICATION & ROLES ---
ADMINS = {
    "sawer khan": {"pwd": "sawer123", "role": "Manager"},
    "tariq": {"pwd": "tariq456", "role": "Manager"},
    "agent1": {"pwd": "pindi786", "role": "Agent"}
}

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Enterprise ERP Login")
    u = st.text_input("Username").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in ADMINS and ADMINS[u]['pwd'] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.session_state.role = ADMINS[u]['role']
            st.rerun()
    st.stop()

# --- 3. SIDEBAR NAVIGATION (Same Style, More Power) ---
st.sidebar.title(f"🏢 {st.session_state.user.title()}")
st.sidebar.write(f"Access Level: **{st.session_state.role}**")
nav = st.sidebar.radio("ERP MODULES", ["📊 Dashboard", "🏠 Inventory Engine", "👥 Client CRM & Match", "💰 Accounts Ledger"])

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()

# --- 4. DASHBOARD ---
if nav == "📊 Dashboard":
    st.title("Market Analytics")
    inv = supabase.table("inventory").select("*").execute().data
    cli = supabase.table("clients").select("*").execute().data
    acc = supabase.table("accounts").select("*").execute().data
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Properties", len(inv) if inv else 0)
    c2.metric("Total Clients", len(cli) if cli else 0)
    
    if acc and st.session_state.role == "Manager":
        df_acc = pd.DataFrame(acc)
        profit = df_acc[df_acc['type']=='Income']['amount'].sum() - df_acc[df_acc['type']=='Expense']['amount'].sum()
        c3.metric("Net Profit", f"{profit:,} PKR")

# --- 5. INVENTORY ENGINE ---
elif nav == "🏠 Inventory Engine":
    st.title("Property Management")
    with st.expander("➕ Add New Premium Listing"):
        with st.form("inv_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            cat = c1.selectbox("Category", ["Residential", "Commercial", "Plot"])
            dtype = c2.selectbox("Type", ["Sale", "Rent"])
            area = c3.text_input("Area / Sector (e.g. DHA 2, G-11)")
            
            p1, p2, p3 = st.columns(3)
            price = p1.number_input("Demand (PKR)", min_value=0)
            beds = p2.number_input("Beds", 0, 10)
            marla = p3.number_input("Size (Marla)", 0.1)
            
            maps = st.text_input("Google Maps Link")
            owner = st.text_input("Owner Name & Contact")
            
            if st.form_submit_button("Publish Listing"):
                supabase.table("inventory").insert({
                    "property_category": cat, "property_type": dtype, "area": area,
                    "price": price, "beds": beds, "marla": marla, "owner_name": owner,
                    "location_link": maps, "added_by": st.session_state.user
                }).execute()
                st.success("Property Added!")

    # Search List
    st.subheader("📂 All Records")
    res = supabase.table("inventory").select("*").execute().data
    if res:
        for p in res:
            with st.container(border=True):
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"### {p['area']} - {p['price']:,} PKR")
                col_a.write(f"**Specs:** {p['marla']} Marla | {p['beds']} Beds | Owner: {p['owner_name']}")
                if p.get('location_link'): col_a.link_button("📍 Map", p['location_link'])
                if col_b.button("Delete", key=f"del_{p['id']}"):
                    supabase.table("inventory").delete().eq("id", p['id']).execute()
                    st.rerun()

# --- 6. CLIENT CRM & SMART MATCH ---
elif nav == "👥 Client CRM & Match":
    st.title("Client Lead Management")
    t1, t2 = st.tabs(["🆕 Register Client", "🎯 Intelligent Match Engine"])
    
    with t1:
        with st.form("cli_form", clear_on_submit=True):
            c_name = st.text_input("Client Name")
            c_phone = st.text_input("WhatsApp Number (e.g. 923001234567)")
            c_budget = st.number_input("Max Budget", min_value=0)
            c_req = st.selectbox("Req Type", ["Rent", "Sale"])
            c_status = st.selectbox("Priority", ["Hot 🔥", "Warm", "Cold"])
            if st.form_submit_button("Save Lead"):
                supabase.table("clients").insert({
                    "client_name": c_name, "client_contact": c_phone, 
                    "max_budget": c_budget, "demand_type": c_req, "status": c_status
                }).execute()
                st.success("Client Registered!")

    with t2:
        cls = supabase.table("clients").select("*").execute().data
        if cls:
            sel_c = st.selectbox("Select Client", [x['client_name'] for x in cls])
            c_det = next(x for x in cls if x['client_name'] == sel_c)
            
            # ADVANCED MATCHING LOGIC (Budget + Type)
            matches = supabase.table("inventory").select("*")\
                .eq("property_type", c_det['demand_type'])\
                .lte("price", c_det['max_budget'])\
                .execute().data
            
            if matches:
                st.write(f"Found {len(matches)} matches for {sel_c}:")
                for m in matches:
                    with st.container(border=True):
                        st.write(f"🏠 **{m['area']}** ({m['price']:,} PKR)")
                        # WhatsApp One-Click Share
                        msg = f"Salam {c_det['client_name']}, hamare pas {m['area']} mein aik zabardast option hai. Price: {m['price']:,} PKR."
                        wa_url = f"https://wa.me/{c_det['client_contact']}?text={quote(msg)}"
                        st.link_button("💬 Share to WhatsApp", wa_url)

# --- 7. ACCOUNTS LEDGER (Admin Only) ---
elif nav == "💰 Accounts Ledger":
    st.title("Finance & Commissions")
    if st.session_state.role != "Manager":
        st.error("Access Restricted! Sirf Managers ye dekh sakte hain.")
    else:
        with st.form("acc_form"):
            atyp = st.selectbox("Type", ["Income", "Expense"])
            acat = st.selectbox("Category", ["Commission", "Petrol", "Marketing", "Tea/Food"])
            aamt = st.number_input("Amount", min_value=0)
            adesc = st.text_input("Details")
            if st.form_submit_button("Save Record"):
                supabase.table("accounts").insert({"type": atyp, "category": acat, "amount": aamt, "description": adesc}).execute()
                st.success("Account updated!")
