import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# --- SETTINGS & THEME ---
st.set_page_config(page_title="Pindi-Isloo Realty Pro ERP", layout="wide", page_icon="🏢")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; }
    .stButton>button { border-radius: 5px; height: 3em; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #007bff; color: white; border: none; }
    .css-1kyx92n { background-color: #1e293b; } /* Sidebar color */
    </style>
    """, unsafe_allow_html=True)

# --- DB CONNECTION ---
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Database connection failed. Check your Secrets.")
    st.stop()

# --- AUTH SYSTEM ---
ADMINS = {"sawer khan": "sawer123", "tariq": "tariq456", "admin3": "pindi786"}

if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("https://cdn-icons-png.flaticon.com/512/609/609803.png", width=100)
        st.title("Realty Pro ERP Login")
        with st.container(border=True):
            u = st.text_input("Username").lower().strip()
            p = st.text_input("Password", type="password")
            if st.button("Access Dashboard", use_container_width=True):
                if u in ADMINS and ADMINS[u] == p:
                    st.session_state.auth, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Access Denied.")
    st.stop()

# --- NAVIGATION ---
with st.sidebar:
    st.title("🏢 Realty Pro v2.0")
    st.write(f"Welcome, **{st.session_state.user.title()}**")
    menu = st.radio("MAIN NAVIGATION", ["📊 Performance Dashboard", "🏗️ Listing Engine", "🔍 Advanced Search", "👥 CRM & Matches", "⚙️ Admin Settings"])
    if st.button("🔒 Logout"):
        st.session_state.auth = False
        st.rerun()

# --- 1. DASHBOARD (PRO) ---
if menu == "📊 Performance Dashboard":
    st.title("Real Estate Analytics")
    
    inv = supabase.table("inventory").select("*").execute().data
    df = pd.DataFrame(inv) if inv else pd.DataFrame()

    # High-Level Metrics
    m1, m2, m3, m4 = st.columns(4)
    if not df.empty:
        m1.metric("Total Inventory", len(df))
        m2.metric("Available for Rent", len(df[df['property_type']=='Rent']))
        m3.metric("Available for Sale", len(df[df['property_type']=='Sale']))
        m4.metric("Active Deals", len(df[df['status']!='Available']))
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📍 Hot Locations (Inventory Density)")
        if not df.empty:
            st.bar_chart(df['area'].value_counts())
    with c2:
        st.subheader("💰 Market Valuation")
        if not df.empty:
            st.write("Average Demand by Property Type")
            st.dataframe(df.groupby('sub_type')['price'].mean().map('{:,.0f} PKR'.format), use_container_width=True)

# --- 2. LISTING ENGINE (DETAILED FORM) ---
elif menu == "🏗️ Listing Engine":
    st.title("Add New Premium Property")
    with st.form("heavy_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        cat = col1.selectbox("Category", ["Residential", "Commercial", "Industrial", "Plot"])
        deal = col2.selectbox("Deal Type", ["Sale", "Rent"])
        sub = col3.selectbox("Sub-Type", ["House", "Flat/Apartment", "Shop", "Office", "Warehouse", "Penthouse", "Plot File", "Plaza"])

        col4, col5 = st.columns([2, 1])
        area = col4.text_input("Location / Sector (e.g. DHA Phase 2, Sector F-6)")
        marla = col5.number_input("Size (Marla/Kanal)", min_value=0.1)

        addr = st.text_area("Full Address / Internal Plot Number")

        col6, col7, col8 = st.columns(3)
        price = col6.number_input("Asking Price (PKR)", min_value=0, step=100000)
        beds = col7.number_input("Bedrooms", 0, 20)
        baths = col8.number_input("Bathrooms", 0, 20)

        st.subheader("🛠️ Technical Utilities")
        u1, u2, u3, u4 = st.columns(4)
        gas = u1.selectbox("Gas", ["Separate Meter", "Combined Meter", "No Gas"])
        water = u2.selectbox("Water", ["Boring", "Govt Supply", "Supply+Boring", "Tanker"])
        elec = u3.selectbox("Electricity", ["Separate", "Combined", "3-Phase", "Solar Installed"])
        portion = u4.selectbox("Portion", ["Full", "Ground", "First", "Second", "Basement"])

        st.subheader("✨ Premium Amenities")
        amenities = st.multiselect("Select Features", ["Car Parking", "CCTV Security", "Corner Plot", "Park Facing", "Main Blvd", "Basement", "Lift/Elevator", "Servant Quarter"])

        st.subheader("👤 Owner / Source Data")
        o1, o2 = st.columns(2)
        oname = o1.text_input("Owner Name")
        ocont = o2.text_input("Owner Contact (WhatsApp/Call)")

        if st.form_submit_button("🚀 PUBLISH LISTING"):
            data = {
                "added_by": st.session_state.user, "property_category": cat, "property_type": deal,
                "sub_type": sub, "area": area, "address": addr, "price": price, "marla": marla,
                "beds": beds, "baths": baths, "gas": gas, "water": water, "electricity": elec,
                "portion": portion, "amenities": amenities, "owner_name": oname, "owner_contact": ocont
            }
            supabase.table("inventory").insert(data).execute()
            st.balloons()
            st.success("Listing is now Live!")

# --- 3. ADVANCED SEARCH & MANAGER ---
elif menu == "🔍 Advanced Search":
    st.title("Search & Manage Records")
    
    # Advanced Filters
    with st.expander("🛠️ Advanced Filters", expanded=True):
        f1, f2, f3, f4 = st.columns(4)
        f_cat = f1.multiselect("Category", ["Residential", "Commercial", "Industrial"])
        f_deal = f2.selectbox("Deal", ["All", "Sale", "Rent"])
        f_min, f_max = f3.slider("Price Range (Mln)", 0, 500, (0, 500))
        f_area = f4.text_input("Search Area (DHA, Bahria...)")

    inv = supabase.table("inventory").select("*").execute().data
    if inv:
        for p in inv:
            # Simple filtering logic
            if (f_deal == "All" or p['property_type'] == f_deal) and (f_area.lower() in p['area'].lower()):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        st.markdown(f"### {p['price']:,} PKR")
                        st.caption(f"ID: {p['id']} | {p['property_type']}")
                    with c2:
                        st.write(f"📍 **{p['area']}** ({p['sub_type']})")
                        st.write(f"📐 {p['marla']} Marla | 🛏️ {p['beds']} Beds | 🚿 {p['baths']} Baths")
                        st.caption(f"Amenities: {', '.join(p['amenities']) if p['amenities'] else 'None'}")
                    with c3:
                        st.write(f"📞 {p['owner_contact']}")
                        if st.button("Delete", key=f"del_{p['id']}"):
                            supabase.table("inventory").delete().eq("id", p['id']).execute()
                            st.rerun()
