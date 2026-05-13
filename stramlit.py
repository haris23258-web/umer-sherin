import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote
import time

# --- 1. SETUP & DATABASE ---
st.set_page_config(page_title="Pro-Level Real Estate ERP", layout="wide")

try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Connection Error! DB link missing.")
    st.stop()

# --- 2. THEME & STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN & ROLES ---
ADMINS = {"sawer khan": "sawer123", "tariq": "tariq456"}
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏛️ Enterprise Property Portal")
    with st.container(border=True):
        u = st.text_input("User ID").lower().strip()
        p = st.text_input("Password", type="password")
        if st.button("Secure Login"):
            if u in ADMINS and ADMINS[u] == p:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

# --- 4. NAVIGATION ---
with st.sidebar:
    st.title("ERP Control")
    st.write(f"Active: **{st.session_state.user.title()}**")
    menu = st.radio("SELECT MODULE", [
        "📈 Sales & Profit", 
        "🏗️ Inventory Bank", 
        "🎯 Lead Matcher", 
        "👥 Clients & CRM",
        "⚙️ System Settings"
    ])
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

# --- 5. SALES & PROFIT (Admin Dashboard) ---
if menu == "📈 Sales & Profit":
    st.title("Financial Intelligence")
    # Fetch Data
    acc = supabase.table("accounts").select("*").execute().data
    inv = supabase.table("inventory").select("*").execute().data
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Properties", len(inv) if inv else 0)
    
    if acc:
        df = pd.DataFrame(acc)
        income = df[df['type']=='Income']['amount'].sum()
        expense = df[df['type']=='Expense']['amount'].sum()
        c2.metric("Gross Revenue", f"{income:,}")
        c3.metric("Total Expenses", f"{expense:,}")
        c4.metric("Net Profit", f"{income-expense:,}")
    
    st.divider()
    st.subheader("Property Trends")
    if inv:
        df_inv = pd.DataFrame(inv)
        st.area_chart(df_inv['area'].value_counts())

# --- 6. INVENTORY BANK (Advance) ---
elif menu == "🏗️ Inventory Bank":
    st.title("Property Inventory")
    t1, t2 = st.tabs(["➕ Add Listing", "📦 Manage Stock"])
    
    with t1:
        with st.form("main_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            cat = col1.selectbox("Category", ["Residential", "Commercial", "Plots"])
            deal = col2.selectbox("Deal Type", ["Sale", "Rent"])
            area = col3.text_input("Exact Location")
            
            p1, p2, p3 = st.columns(3)
            price = p1.number_input("Demand (PKR)", min_value=0)
            marla = p2.number_input("Size (Marla)", min_value=0.0)
            status = p3.selectbox("Status", ["Available", "Hold", "Sold"])
            
            o1, o2 = st.columns(2)
            owner = o1.text_input("Owner Name")
            contact = o2.text_input("Owner Contact")
            
            img_url = st.text_input("Main Image URL")
            maps = st.text_input("Google Maps Link")
            
            if st.form_submit_button("🚀 LOCK PROPERTY"):
                supabase.table("inventory").insert({
                    "property_category": cat, "property_type": deal, "area": area,
                    "price": price, "marla": marla, "status": status, "owner_name": owner,
                    "owner_contact": contact, "location_link": maps, "image_url": img_url,
                    "added_by": st.session_state.user
                }).execute()
                st.success("Property Saved to Secure Cloud!")

    with t2:
        res = supabase.table("inventory").select("*").execute().data
        if res:
            df_res = pd.DataFrame(res)
            st.dataframe(df_res[['area', 'price', 'status', 'owner_name']], use_container_width=True)
            for p in res:
                with st.container(border=True):
                    c_img, c_txt = st.columns([1, 2])
                    if p.get('image_url'): c_img.image(p['image_url'], use_container_width=True)
                    else: c_img.write("No Image Available")
                    
                    c_txt.subheader(f"{p['area']} - {p['price']:,} PKR")
                    c_txt.write(f"Type: {p['property_category']} | {p['marla']} Marla | Status: `{p['status']}`")
                    
                    btn1, btn2, btn3 = c_txt.columns(3)
                    if p.get('location_link'): btn1.link_button("📍 Map", p['location_link'])
                    if btn2.button("❌ Delete", key=f"del_{p['id']}"):
                        supabase.table("inventory").delete().eq("id", p['id']).execute()
                        st.rerun()

# --- 7. LEAD MATCHER (AI Logic) ---
elif menu == "🎯 Lead Matcher":
    st.title("Smart Match Engine")
    clients = supabase.table("clients").select("*").execute().data
    if clients:
        target = st.selectbox("Select Client", [x['client_name'] for x in clients])
        c = next(x for x in clients if x['client_name'] == target)
        
        st.write(f"Finding matches for **{c['client_name']}** (Budget: {c['max_budget']:,} | Req: {c['demand_type']})")
        
        matches = supabase.table("inventory").select("*").eq("property_type", c['demand_type']).lte("price", c['max_budget']).execute().data
        
        if matches:
            for m in matches:
                with st.container(border=True):
                    st.write(f"🏠 **{m['area']}** - Price: {m['price']:,} PKR")
                    # Match Score Logic
                    score = 100 if m['price'] <= (c['max_budget'] * 0.9) else 85
                    st.progress(score/100, text=f"Match Score: {score}%")
                    
                    wa_msg = f"Salam {c['client_name']}, hamare paas {m['area']} mein aik perfect option hai. Price: {m['price']:,}."
                    st.link_button("💬 Share via WhatsApp", f"https://wa.me/{c['client_contact']}?text={quote(wa_msg)}")
        else: st.warning("No matches found.")

# --- 8. CLIENTS & CRM ---
elif menu == "👥 Clients & CRM":
    st.title("Client Relationship Management")
    with st.form("client_form"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Client Name")
        phone = c2.text_input("WhatsApp (92...)")
        budget = c3.number_input("Max Budget", min_value=0)
        
        r1, r2 = st.columns(2)
        req = r1.selectbox("Requirement", ["Sale", "Rent"])
        status = r2.selectbox("Lead Status", ["Hot 🔥", "Warm ⚡", "Cold ❄️"])
        
        if st.form_submit_button("Save Lead"):
            supabase.table("clients").insert({
                "client_name": name, "client_contact": phone, "max_budget": budget, 
                "demand_type": req, "status": status
            }).execute()
            st.success("Lead Added!")
