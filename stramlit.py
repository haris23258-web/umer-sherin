import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote
from datetime import datetime

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="Estate Pro v8.0 | Enterprise ERP", layout="wide")

# Modern Professional Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .property-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-top: 5px solid #1e40af; margin-bottom: 20px;
    }
    .metric-card {
        background: #ffffff; padding: 15px; border-radius: 10px;
        border: 1px solid #e2e8f0; text-align: center;
    }
    .status-pill {
        padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600;
    }
    .available { background: #dcfce7; color: #166534; }
    .sold { background: #fee2e2; color: #991b1b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DB CONNECTION ---
try:
    # Ensure these are in your Streamlit Secrets
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error(f"⚠️ Connection Failed: {e}")
    st.stop()

# --- 3. ADVANCED AUTH SYSTEM ---
USER_DB = {
    "sawer khan": {"role": "Admin", "pin": "sawer123"},
    "tariq": {"role": "Admin", "pin": "tariq456"},
    "agent": {"role": "Agent", "pin": "786"}
}

if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🛡️ Enterprise Realty Gateway")
    with st.container(border=True):
        uid = st.text_input("User ID").lower().strip()
        upin = st.text_input("Access PIN", type="password")
        if st.button("Enter System", use_container_width=True):
            if uid in USER_DB and USER_DB[uid]["pin"] == upin:
                st.session_state.authenticated = True
                st.session_state.user = uid
                st.session_state.role = USER_DB[uid]["role"]
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

# --- 4. NAVIGATION ---
with st.sidebar:
    st.title("🏗️ Estate Pro v8")
    st.write(f"Logged in: **{st.session_state.user.upper()}**")
    st.caption(f"Access Level: {st.session_state.role}")
    st.divider()
    nav = st.radio("ERP MODULES", [
        "📊 Analytics Dashboard", 
        "🏠 Inventory Engine", 
        "🎯 AI Deal Matcher", 
        "💰 Finance & Payroll",
        "📑 Activity Logs"
    ])
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. ANALYTICS MODULE ---
if nav == "📊 Analytics Dashboard":
    st.title("Market Intelligence Dashboard")
    
    # Fetch Data
    inv = supabase.table("inventory").select("*").execute().data
    cli = supabase.table("clients").select("*").execute().data
    acc = supabase.table("accounts").select("*").execute().data
    
    # KPI Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1: st.metric("Live Inventory", len(inv) if inv else 0)
    with kpi2: st.metric("Hot Leads", len(cli) if cli else 0)
    
    if st.session_state.role == "Admin" and acc:
        df_acc = pd.DataFrame(acc)
        rev = df_acc[df_acc['type']=='Income']['amount'].sum()
        with kpi3: st.metric("Total Revenue", f"{rev:,} PKR")
    
    st.divider()
    # Visuals
    c_left, c_right = st.columns(2)
    if inv:
        df_i = pd.DataFrame(inv)
        with c_left:
            st.subheader("📍 Inventory by Location")
            st.bar_chart(df_i['area'].value_counts())
        with c_right:
            st.subheader("🏠 Type Distribution")
            st.bar_chart(df_i['property_type'].value_counts())

# --- 6. INVENTORY ENGINE (Cards UI) ---
elif nav == "🏠 Inventory Engine":
    st.title("Property Bank")
    t1, t2 = st.tabs(["➕ Add New Asset", "🔍 Browse Assets"])
    
    with t1:
        with st.form("add_prop", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            area = col1.text_input("Area (e.g. DHA Phase 2)")
            price = col2.number_input("Demand (PKR)", min_value=0)
            m_size = col3.number_input("Size (Marla)", 1.0)
            
            col4, col5, col6 = st.columns(3)
            p_type = col4.selectbox("Type", ["Sale", "Rent"])
            p_cat = col5.selectbox("Category", ["House", "Plot", "Flat", "Commercial"])
            status = col6.selectbox("Status", ["Available", "Hold"])
            
            o_name = st.text_input("Owner Name")
            o_phone = st.text_input("Owner Contact")
            
            if st.form_submit_button("PUBLISH TO ERP"):
                supabase.table("inventory").insert({
                    "area": area, "price": price, "marla": m_size, "property_type": p_type,
                    "sub_type": p_cat, "status": status, "owner_name": o_name, 
                    "owner_contact": o_phone, "added_by": st.session_state.user
                }).execute()
                supabase.table("activity_logs").insert({"user": st.session_state.user, "action": f"Added {m_size} Marla in {area}"}).execute()
                st.success("Property Synced Globally!")

    with t2:
        search = st.text_input("Search Location...")
        data = supabase.table("inventory").select("*").ilike("area", f"%{search}%").execute().data
        if data:
            for p in data:
                with st.container():
                    st.markdown(f"""
                    <div class="property-card">
                        <span class="status-pill {'available' if p['status']=='Available' else 'sold'}">{p['status']}</span>
                        <h3>📍 {p['area']}</h3>
                        <p><b>{p['marla']} Marla {p['sub_type']}</b> for <b>{p['property_type']}</b></p>
                        <h4 style="color:#1e40af;">{p['price']:,} PKR</h4>
                        <hr>
                        <p>👤 {p['owner_name']} | 📞 {p['owner_contact']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.session_state.role == "Admin" and p['status'] == "Available":
                        if st.button(f"Mark as Sold", key=f"sold_{p['id']}"):
                            supabase.table("inventory").update({"status": "Sold"}).eq("id", p['id']).execute()
                            st.rerun()

# --- 7. AI DEAL MATCHER ---
elif nav == "🎯 AI Deal Matcher":
    st.title("Smart Match & Auto-Alert")
    clients = supabase.table("clients").select("*").execute().data
    if clients:
        sel_c = st.selectbox("Select Target Client", [x['client_name'] for x in clients])
        c = next(x for x in clients if x['client_name'] == sel_c)
        
        # Deep Match Logic
        matches = supabase.table("inventory").select("*")\
            .eq("property_type", c['demand_type'])\
            .lte("price", c['max_budget'] * 1.1)\
            .eq("status", "Available").execute().data
        
        if matches:
            for m in matches:
                # Match Score Logic
                score = 100
                if m['price'] > c['max_budget']: score -= 15
                
                with st.container(border=True):
                    st.write(f"### Match Score: {score}%")
                    st.progress(score/100)
                    st.write(f"🏠 **{m['area']}** | Price: {m['price']:,} PKR")
                    
                    wa_text = f"Salam {sel_c}, we found a matching property for you in {m['area']}. Demand: {m['price']:,}. Contact us for details."
                    st.link_button("📲 Push to WhatsApp", f"https://wa.me/{c['client_contact']}?text={quote(wa_text)}")
        else:
            st.warning("No properties matching this client's profile.")

# --- 8. FINANCE & PAYROLL ---
elif nav == "💰 Finance & Payroll":
    st.title("Financial Ledger")
    if st.session_state.role != "Admin":
        st.error("Admin Access Required")
    else:
        with st.form("ledger_entry"):
            f1, f2 = st.columns(2)
            t_type = f1.selectbox("Transaction", ["Income", "Expense"])
            amt = f2.number_input("Amount (PKR)", min_value=0)
            desc = st.text_area("Details (Include Deal IDs)")
            if st.form_submit_button("Record Transaction"):
                supabase.table("accounts").insert({"type": t_type, "amount": amt, "description": desc}).execute()
                st.success("Ledger Updated!")

# --- 9. ACTIVITY LOGS ---
elif nav == "📑 Activity Logs":
    st.title("System Audit Trail")
    if st.session_state.role != "Admin":
        st.error("Access Denied")
    else:
        logs = supabase.table("activity_logs").select("*").order("created_at", desc=True).execute().data
        if logs:
            st.table(pd.DataFrame(logs)[['created_at', 'user', 'action']])
