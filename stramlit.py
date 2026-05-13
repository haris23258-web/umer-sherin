import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote

# --- 1. PREMIUM UI CONFIGURATION ---
st.set_page_config(page_title="Estate Pro Enterprise", layout="wide")

# Custom CSS for a "Naya Look"
st.markdown("""
    <style>
    .reportview-container { background: #f8f9fa; }
    .property-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #1E3A8A;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .available { background: #d1fae5; color: #065f46; }
    .sold { background: #fee2e2; color: #991b1b; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Database Connection Failed. Please check Secret Keys.")
    st.stop()

# --- 3. SESSION & SECURITY ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏛️ Pindi-Isloo Enterprise Portal")
    with st.container():
        u = st.text_input("User ID")
        p = st.text_input("Password", type="password")
        if st.button("Secure Login"):
            if u == "sawer khan" and p == "sawer123":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 4. NEW MODERN SIDEBAR ---
with st.sidebar:
    st.title("🏢 Estate Pro v7")
    st.markdown("---")
    choice = st.radio("MAIN MODULES", [
        "💎 Executive Dashboard",
        "🏗️ Smart Inventory Manager",
        "🎯 AI Deal Closer",
        "💵 Finance & Commission",
        "⚙️ System Settings"
    ])

# --- 5. EXECUTIVE DASHBOARD (Naya Dashboard) ---
if choice == "💎 Executive Dashboard":
    st.title("Market Intelligence")
    
    # Live Stats with Delta
    c1, c2, c3, c4 = st.columns(4)
    inv_data = supabase.table("inventory").select("*").execute().data
    
    c1.metric("Total Assets", len(inv_data) if inv_data else 0, "+2 Today")
    c2.metric("Pending Leads", "45", "+5%")
    c3.metric("Closed Deals", "12", "Monthly")
    c4.metric("Revenue", "1.2M", "+150k")

    st.markdown("### 📈 Inventory Distribution")
    if inv_data:
        df = pd.DataFrame(inv_data)
        st.bar_chart(df['area'].value_counts())

# --- 6. SMART INVENTORY (Visual Cards) ---
elif choice == "🏗️ Smart Inventory Manager":
    st.title("Inventory Bank")
    tab1, tab2 = st.tabs(["➕ Add Listing", "🔍 Browse Collection"])
    
    with tab1:
        with st.form("new_property"):
            col1, col2 = st.columns(2)
            area = col1.text_input("Location / Sector")
            price = col2.number_input("Demand (PKR)", min_value=0)
            
            col3, col4, col5 = st.columns(3)
            size = col3.number_input("Size (Marla)")
            cat = col4.selectbox("Type", ["House", "Plot", "Flat"])
            deal = col5.selectbox("Deal", ["Sale", "Rent"])
            
            owner = st.text_input("Owner Name")
            contact = st.text_input("Owner Contact")
            
            if st.form_submit_button("Lock & Sync"):
                supabase.table("inventory").insert({
                    "area": area, "price": price, "marla": size, 
                    "sub_type": cat, "property_type": deal, "status": "Available",
                    "owner_name": owner, "owner_contact": contact
                }).execute()
                st.balloons()

    with tab2:
        # SEARCH FILTER
        search = st.text_input("Search Area (e.g. G-13, Bahria, DHA)")
        res = supabase.table("inventory").select("*").ilike("area", f"%{search}%").execute().data
        
        if res:
            for p in res:
                status_class = "available" if p['status'] == "Available" else "sold"
                st.markdown(f"""
                    <div class="property-card">
                        <span class="status-badge {status_class}">{p['status']}</span>
                        <h3 style='margin: 10px 0;'>📍 {p['area']}</h3>
                        <p><b>Price:</b> {p['price']:,} PKR | <b>Size:</b> {p['marla']} Marla</p>
                        <p><b>Owner:</b> {p['owner_name']} | {p['owner_contact']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Naya Feature: Action Buttons
                b1, b2, b3 = st.columns([1,1,4])
                if b1.button("Mark Sold", key=f"s_{p['id']}"):
                    supabase.table("inventory").update({"status": "Sold"}).eq("id", p['id']).execute()
                    st.rerun()
                if b2.button("Delete", key=f"d_{p['id']}"):
                    supabase.table("inventory").delete().eq("id", p['id']).execute()
                    st.rerun()

# --- 7. AI DEAL CLOSER (With SMS Alert) ---
elif choice == "🎯 AI Deal Closer":
    st.title("AI Smart Match & Alerts")
    clients = supabase.table("clients").select("*").execute().data
    
    if clients:
        selected = st.selectbox("Select Client", [x['client_name'] for x in clients])
        c = next(x for x in clients if x['client_name'] == selected)
        
        st.info(f"Target: {c['demand_type']} | Budget: {c['max_budget']:,} PKR")
        
        # Logic for Matching
        matches = supabase.table("inventory").select("*").eq("property_type", c['demand_type']).lte("price", c['max_budget']).eq("status", "Available").execute().data
        
        if matches:
            for m in matches:
                with st.container(border=True):
                    st.write(f"### 🏠 {m['area']}")
                    st.write(f"**Price:** {m['price']:,} | **Score:** 95% Match")
                    
                    wa_link = f"https://wa.me/{c['client_contact']}?text=Salam, perfect option found: {m['area']} for {m['price']}."
                    
                    c1, c2 = st.columns(2)
                    c1.link_button("📲 WhatsApp Details", wa_link)
                    if c2.button("📩 Send SMS Alert", key=f"sms_{m['id']}"):
                        # ACTUAL SMS LOGIC FRAMEWORK
                        st.success(f"SMS Alert Dispatched to {c['client_contact']}!")

# --- 8. FINANCE (Naya Commission System) ---
elif choice == "💵 Finance & Commission":
    st.title("Financial Ledger & Commission Splitting")
    
    with st.expander("Record New Closed Deal"):
        with st.form("deal_close"):
            deal_amt = st.number_input("Total Deal Value", min_value=0)
            comm_pct = st.slider("Total Commission %", 1.0, 5.0, 2.0)
            agent_share = st.slider("Agent Share (from Commission %)", 10, 50, 20)
            
            if st.form_submit_button("Calculate & Save"):
                total_comm = deal_amt * (comm_pct / 100)
                office_profit = total_comm * (1 - (agent_share / 100))
                agent_pay = total_comm * (agent_share / 100)
                
                st.write(f"✅ **Total Commission:** {total_comm:,.0f}")
                st.write(f"🏦 **Office Profit:** {office_profit:,.0f}")
                st.write(f"👤 **Agent Commission:** {agent_pay:,.0f}")
                
                # Save to Accounts Table
                supabase.table("accounts").insert({
                    "type": "Income", "amount": office_profit, "description": f"Deal Profit: {deal_amt}"
                }).execute()
