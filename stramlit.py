import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote

# --- 1. CONNECTION ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Database connection failed!")
    st.stop()

# --- 2. THEME & SETTINGS ---
st.set_page_config(page_title="Realty Pro ERP", layout="wide")

# --- 3. AUTH SYSTEM (Simple & Solid) ---
ADMINS = {"sawer khan": "sawer123", "tariq": "tariq456", "admin3": "pindi786"}
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ Enterprise Portal Login")
    u = st.text_input("Username").lower().strip()
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in ADMINS and ADMINS[u] == p:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else: st.error("Access Denied.")
    st.stop()

# --- 4. NAVIGATION (Wahi Simple Style) ---
menu = st.sidebar.radio("MENU", [
    "📊 Dashboard", 
    "🏠 Inventory Engine", 
    "👥 Client CRM & Matching", 
    "💰 Accounts & Profits"
])

if st.sidebar.button("Logout"):
    st.session_state.auth = False
    st.rerun()

# --- 5. DASHBOARD ---
if menu == "📊 Dashboard":
    st.title(f"Welcome, {st.session_state.user.title()}")
    inv = supabase.table("inventory").select("*").execute().data
    cli = supabase.table("clients").select("*").execute().data
    acc = supabase.table("accounts").select("*").execute().data
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Properties", len(inv) if inv else 0)
    c2.metric("Total Clients", len(cli) if cli else 0)
    
    if acc:
        df_a = pd.DataFrame(acc)
        profit = df_a[df_a['type']=='Income']['amount'].sum() - df_a[df_a['type']=='Expense']['amount'].sum()
        c3.metric("Net Profit", f"{profit:,} PKR")
    
    st.divider()
    if inv:
        st.subheader("Area Wise Inventory")
        st.bar_chart(pd.DataFrame(inv)['area'].value_counts())

# --- 6. INVENTORY ENGINE (Heavy Form with Maps & Images) ---
elif menu == "🏠 Inventory Engine":
    st.title("Property Management")
    t1, t2 = st.tabs(["➕ Add New Property", "📂 Search & View Inventory"])
    
    with t1:
        with st.form("inventory_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            cat = col1.selectbox("Category", ["Residential", "Commercial", "Plot"])
            deal = col2.selectbox("Deal Type", ["Sale", "Rent"])
            sub = col3.selectbox("Sub-Type", ["House", "Flat", "Shop", "Office", "Plot"])

            area = st.text_input("Location (e.g. DHA Phase 2, G-11)")
            price = st.number_input("Asking Price (PKR)", min_value=0)
            
            c4, c5 = st.columns(2)
            owner = c4.text_input("Owner Name & Contact")
            maps = c5.text_input("Google Maps Link")
            
            # Additional Details
            st.subheader("Technical Details")
            d1, d2, d3 = st.columns(3)
            beds = d1.number_input("Beds", 0, 10)
            marla = d2.number_input("Marla", 0.0)
            utilities = d3.multiselect("Utilities", ["Gas", "Water", "Electricity", "Fiber Internet"])

            if st.form_submit_button("🚀 PUBLISH PROPERTY"):
                supabase.table("inventory").insert({
                    "property_category": cat, "property_type": deal, "sub_type": sub,
                    "area": area, "price": price, "owner_name": owner, 
                    "location_link": maps, "beds": beds, "marla": marla, "added_by": st.session_state.user
                }).execute()
                st.success("Property Saved Successfully!")

    with t2:
        res = supabase.table("inventory").select("*").execute().data
        if res:
            for p in res:
                with st.container(border=True):
                    st.write(f"### {p['area']} - {p['price']:,} PKR")
                    st.write(f"**Type:** {p['sub_type']} | **Size:** {p['marla']} Marla | **Owner:** {p['owner_name']}")
                    if p.get('location_link'): st.link_button("📍 Open in Google Maps", p['location_link'])
                    if st.button("Delete Property", key=f"del_{p['id']}"):
                        supabase.table("inventory").delete().eq("id", p['id']).execute()
                        st.rerun()

# --- 7. CLIENT CRM & SMART MATCH ---
elif menu == "👥 Client CRM & Matching":
    st.title("Client CRM")
    tab1, tab2 = st.tabs(["➕ Register Client", "🎯 Smart Matching Engine"])
    
    with tab1:
        with st.form("client_form", clear_on_submit=True):
            name = st.text_input("Client Name")
            phone = st.text_input("Phone Number (92...)")
            budget = st.number_input("Max Budget", min_value=0)
            req = st.selectbox("Requirement", ["Rent", "Sale"])
            if st.form_submit_button("Save Client"):
                supabase.table("clients").insert({
                    "client_name": name, "client_contact": phone, "max_budget": budget, "demand_type": req
                }).execute()
                st.success("Client Added to Pipeline!")

    with tab2:
        clients = supabase.table("clients").select("*").execute().data
        if clients:
            selected = st.selectbox("Select Client", [x['client_name'] for x in clients])
            c_data = next(x for x in clients if x['client_name'] == selected)
            
            # Logic: Match price and deal type
            matches = supabase.table("inventory").select("*").eq("property_type", c_data['demand_type']).lte("price", c_data['max_budget']).execute().data
            
            if matches:
                for m in matches:
                    with st.container(border=True):
                        st.write(f"🏠 **{m['area']}** - {m['price']:,} PKR")
                        msg = f"Salam {c_data['client_name']}, hamare paas aap ke liye {m['area']} mein option hai. Price: {m['price']:,}."
                        wa_url = f"https://wa.me/{c_data['client_contact']}?text={quote(msg)}"
                        st.link_button("💬 Send to Client on WhatsApp", wa_url)
            else: st.warning("No matches found yet.")

# --- 8. ACCOUNTS & PROFITS ---
elif menu == "💰 Accounts & Profits":
    st.title("Financial Management")
    with st.form("acc_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        typ = col1.selectbox("Type", ["Income", "Expense"])
        cat = col2.selectbox("Category", ["Commission", "Petrol", "Tea/Food", "Office Rent", "Marketing"])
        amt = st.number_input("Amount", min_value=0)
        desc = st.text_input("Description")
        if st.form_submit_button("Record Transaction"):
            supabase.table("accounts").insert({"type": typ, "category": cat, "amount": amt, "description": desc}).execute()
            st.success("Recorded!")
