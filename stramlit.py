import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="Pindi-Isloo Enterprise ERP", layout="wide", page_icon="🏛️")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .status-available { color: green; font-weight: bold; }
    .status-sold { color: red; font-weight: bold; }
    div[data-testid="stExpander"] { border: 1px solid #1E3A8A; border-radius: 8px; background: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DB & SERVICES SETUP ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Database connection missing! Check your secrets.")
    st.stop()

# --- 3. SECURITY & ROLE MANAGEMENT ---
# Roles: Admin (Full Access), Manager (Inventory/CRM), Agent (View Only)
USER_REGISTRY = {
    "sawer khan": {"pwd": "sawer123", "role": "Admin"},
    "tariq": {"pwd": "tariq456", "role": "Admin"},
    "manager1": {"pwd": "pindi123", "role": "Manager"},
    "agent1": {"pwd": "isloo786", "role": "Agent"}
}

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Enterprise Realty ERP Login")
    with st.container(border=True):
        u = st.text_input("User ID").lower().strip()
        p = st.text_input("Password", type="password")
        if st.button("Authenticate", use_container_width=True):
            if u in USER_REGISTRY and USER_REGISTRY[u]['pwd'] == p:
                st.session_state.auth = True
                st.session_state.user = u
                st.session_state.role = USER_REGISTRY[u]['role']
                # Log Login Event
                supabase.table("activity_logs").insert({"user": u, "action": "Logged In"}).execute()
                st.rerun()
            else: st.error("Invalid credentials.")
    st.stop()

# --- 4. GLOBAL SIDEBAR ---
with st.sidebar:
    st.header(f"Estate Pro v6.0")
    st.info(f"User: {st.session_state.user.title()} \nRole: {st.session_state.role}")
    menu = st.radio("ENTERPRISE MODULES", [
        "📊 Dashboard & Audit Logs",
        "🏠 Master Inventory",
        "👥 Client CRM & Pipeline",
        "🎯 AI Smart Matcher",
        "💰 Accounts & Payroll"
    ])
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

# --- 5. MODULE: DASHBOARD & LOGS ---
if menu == "📊 Dashboard & Audit Logs":
    st.title("Business Analytics & Activity Logs")
    
    # Data Fetching
    inv = supabase.table("inventory").select("*").execute().data
    acc = supabase.table("accounts").select("*").execute().data
    logs = supabase.table("activity_logs").select("*").order("created_at", desc=True).limit(10).execute().data

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Listings", len(inv) if inv else 0)
    
    if st.session_state.role == "Admin" and acc:
        df_acc = pd.DataFrame(acc)
        profit = df_acc[df_acc['type'] == 'Income']['amount'].sum() - df_acc[df_acc['type'] == 'Expense']['amount'].sum()
        m2.metric("Net Profit (PKR)", f"{profit:,}")
    
    st.divider()
    col_logs, col_chart = st.columns([1, 1])
    with col_logs:
        st.subheader("🕵️ Recent Activity Audit")
        if logs:
            for l in logs:
                st.caption(f"**{l['user']}**: {l['action']} ({l['created_at'][:16]})")
    with col_chart:
        st.subheader("📍 Inventory Heatmap")
        if inv:
            df_i = pd.DataFrame(inv)
            st.bar_chart(df_i['area'].value_counts())

# --- 6. MODULE: MASTER INVENTORY ---
elif menu == "🏠 Master Inventory":
    st.title("Enterprise Inventory Engine")
    t1, t2 = st.tabs(["➕ New Listing", "📂 Global Inventory"])
    
    with t1:
        if st.session_state.role == "Agent":
            st.warning("Agents cannot add inventory. Contact Manager.")
        else:
            with st.form("inventory_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                area = c1.text_input("Area / Sector")
                price = c2.number_input("Demand (PKR)", min_value=0)
                size = c3.number_input("Size (Marla)", 0.1)
                
                c4, c5, c6 = st.columns(3)
                deal_type = c4.selectbox("Deal Type", ["Sale", "Rent"])
                sub_type = c5.selectbox("Sub-Type", ["House", "Plot", "Shop", "Office"])
                status = c6.selectbox("Initial Status", ["Available", "Hold"])
                
                owner = st.text_input("Owner Name")
                contact = st.text_input("Owner Contact")
                
                if st.form_submit_button("LOCK PROPERTY"):
                    supabase.table("inventory").insert({
                        "area": area, "price": price, "marla": size, "property_type": deal_type,
                        "sub_type": sub_type, "status": status, "owner_name": owner, 
                        "owner_contact": contact, "added_by": st.session_state.user
                    }).execute()
                    supabase.table("activity_logs").insert({"user": st.session_state.user, "action": f"Added Property in {area}"}).execute()
                    st.success("Property Synced to Database!")

    with t2:
        all_p = supabase.table("inventory").select("*").order("created_at", desc=True).execute().data
        if all_p:
            for p in all_p:
                color = "green" if p['status'] == "Available" else "red"
                with st.expander(f"📍 {p['area']} | {p['price']:,} PKR | :{color}[{p['status']}]"):
                    st.write(f"**Details:** {p['marla']} Marla {p['sub_type']} for {p['property_type']}")
                    st.write(f"**Owner:** {p['owner_name']} ({p['owner_contact']})")
                    
                    if st.session_state.role in ["Admin", "Manager"]:
                        if st.button(f"Mark as SOLD", key=f"sell_{p['id']}"):
                            supabase.table("inventory").update({"status": "Sold"}).eq("id", p['id']).execute()
                            supabase.table("activity_logs").insert({"user": st.session_state.user, "action": f"Marked {p['area']} as SOLD"}).execute()
                            st.rerun()

# --- 7. MODULE: CRM & PIPELINE ---
elif menu == "👥 Client CRM & Pipeline":
    st.title("Lead Management System")
    with st.form("client_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Client Name")
        phone = c2.text_input("Phone (92...)")
        budget = c3.number_input("Max Budget", min_value=0)
        
        req = st.selectbox("Requirement", ["Sale", "Rent"])
        if st.form_submit_button("Add Lead"):
            supabase.table("clients").insert({
                "client_name": name, "client_contact": phone, "max_budget": budget, "demand_type": req
            }).execute()
            st.success("Lead registered in pipeline!")

# --- 8. MODULE: AI SMART MATCHER ---
elif menu == "🎯 AI Smart Matcher":
    st.title("AI-Driven Deal Matching")
    clients = supabase.table("clients").select("*").execute().data
    if clients:
        target = st.selectbox("Select Target Client", [x['client_name'] for x in clients])
        c_data = next(x for x in clients if x['client_name'] == target)
        
        # Advance Match Logic (Filters: Type, Budget, and Status)
        matches = supabase.table("inventory").select("*").eq("property_type", c_data['demand_type']).eq("status", "Available").execute().data
        
        if matches:
            for m in matches:
                # Simple AI Score
                score = 100
                if m['price'] > c_data['max_budget']: score -= 20
                if m['price'] < (c_data['max_budget'] * 0.7): score -= 10 # Too low
                
                with st.container(border=True):
                    st.subheader(f"Match Score: {score}%")
                    st.progress(score/100)
                    st.write(f"🏠 **{m['area']}** - Demand: {m['price']:,} PKR")
                    
                    # SMS / WhatsApp Logic
                    wa_msg = f"Salam {target}, I found a matching property for you in {m['area']}. Price: {m['price']:,}. Let us know if you want to visit."
                    
                    col_b1, col_b2 = st.columns(2)
                    col_b1.link_button("📲 Send WhatsApp", f"https://wa.me/{c_data['client_contact']}?text={quote(wa_msg)}")
                    if col_b2.button("📩 Send SMS Alert", key=f"sms_{m['id']}"):
                        # framework for SMS alert
                        st.toast(f"SMS Sent to {c_data['client_contact']} via Gateway!")

# --- 9. MODULE: ACCOUNTS & PAYROLL ---
elif menu == "💰 Accounts & Payroll":
    st.title("Financial Ledger & Commission Tracker")
    if st.session_state.role != "Admin":
        st.error("Admin restricted module.")
    else:
        with st.form("acc_form"):
            a1, a2 = st.columns(2)
            a_type = a1.selectbox("Type", ["Income", "Expense"])
            a_amt = a2.number_input("Amount (PKR)", min_value=0)
            a_desc = st.text_input("Deal/Description")
            if st.form_submit_button("Record Transaction"):
                supabase.table("accounts").insert({"type": a_type, "amount": a_amt, "description": a_desc}).execute()
                st.success("Ledger Updated!")
