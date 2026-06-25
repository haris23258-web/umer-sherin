import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# Page Layout
st.set_page_config(page_title="DEEWARYN Portal", layout="wide", initial_sidebar_state="collapsed")

# Connection
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- AUTH SYSTEM ---
if "authenticated" not in st.session_state: 
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🏗️ DEEWARYN.COM</h2>", unsafe_allow_html=True)
    
    # Centered login box for mobile
    with st.container():
        user_id = st.text_input("User ID", placeholder="Enter your ID").lower()
        pin = st.text_input("PIN", type="password", placeholder="••••")
        
        # Big touch-friendly login button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 LOG IN", use_container_width=True):
            if user_id in ["sami", "umer", "sawer khan", "tariq"]:
                st.session_state.authenticated = True
                st.session_state.user = user_id
                st.rerun()
            else:
                st.error("Invalid ID or PIN")
    st.stop()

# --- MOBILE STYLING & BOTTOM NAV (CSS) ---
st.markdown("""
<style>
    /* Main Background & Font fixes for clean look */
    .stApp { background-color: #f8fafc; }
    
    #text-input, .stSelectbox, .stButton {
        margin-bottom: 10px !important;
    }
    
    /* Make input fields larger for easy finger tapping */
    input, select, textarea {
        min-height: 48px !important;
        font-size: 16px !important; /* Prevents iOS auto-zoom */
    }
    
    /* Big Touch-Friendly Buttons */
    div.stButton > button {
        height: 52px !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        background-color: #1e3a8a !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(30, 58, 138, 0.15) !important;
    }
    
    /* Elegant Modern Cards for Dashboard Summary */
    .mobile-card {
        background: #ffffff;
        padding: 16px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 15px;
    }
    .card-val { font-size: 26px; font-weight: 800; color: #1e3a8a; }
    .card-lbl { font-size: 13px; color: #64748b; font-weight: 500; margin-top: 4px; }
    
    /* Clean up default Streamlit padding for tight mobile fit */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 5rem !important; }
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION CONTROLLER ---
# Using a top segment select tool which works beautifully on both Mobile and Desktop
menu_options = ["📊 Home", "➕ Quick Entry", "📋 Reports", "🤝 Deals"]
current_tab = st.segmented_control("Navigation Menu", menu_options, default="📊 Home")

# --- DATA FETCHING (Optimized) ---
@st.cache_data(ttl=60)
def get_dashboard_counts():
    try:
        inv = len(supabase.table("inventory").select("id").execute().data or [])
        cli = len(supabase.table("clients").select("id").execute().data or [])
        deals = len(supabase.table("deals").select("id").execute().data or [])
        return inv, cli, deals
    except:
        return 0, 0, 0

inv_count, cli_count, deals_count = get_dashboard_counts()

# --- TAB CONTENT ---

if current_tab == "📊 Home":
    st.markdown(f"<h5>Welcome back, <span style='color:#1e3a8a;'>{st.session_state.user.title()}</span> 👋</h5>", unsafe_allow_html=True)
    st.write("---")
    
    # Mobile Layout Grid (Using columns that stack elegantly)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="mobile-card"><div class="card-val">{inv_count}</div><div class="card-lbl">Properties</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="mobile-card"><div class="card-val">{cli_count}</div><div class="card-lbl">Active Clients</div></div>', unsafe_allow_html=True)
        
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f'<div class="mobile-card"><div class="card-val">{deals_count}</div><div class="card-lbl">Deals Closed</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="mobile-card"><div class="card-val">⚡</div><div class="card-lbl">Quick Sync</div></div>', unsafe_allow_html=True)

    st.write("")
    st.subheader("🎯 Quick Actions")
    
    # Big Shortcut buttons on Home Screen for Mobile Users
    if st.button("➕ Create New Property Entry", use_container_width=True):
        st.info("Tap 'Quick Entry' tab at the top to add data!")
        
    if st.button("📞 Call Support / Admin", use_container_width=True):
        st.success("Opening Support Line...")

elif current_tab == "➕ Quick Entry":
    st.subheader("📝 Mobile Data Entry Form")
    st.write("Fields are optimized for easy typing on mobile keypads.")
    
    with st.form("mobile_entry_form", clear_on_submit=True):
        prop_title = st.text_input("Property Title / Location")
        prop_type = st.selectbox("Type", ["🔑 Plot", "🏢 Flat", "🏡 House", "Commercial"])
        price = st.number_input("Demand Price (PKR)", min_value=0, step=100000)
        client_phone = st.text_input("Client Phone Number")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_with_no_authenticity_token = st.form_submit_button("💾 SAVE DATA", use_container_width=True)
        
        if submitted:
            if prop_title and client_phone:
                # Supabase insert logic
                supabase.table("inventory").insert({
                    "title": prop_title, "type": prop_type, "price": price, "phone": client_phone, "created_at": datetime.now().isoformat()
                }).execute()
                st.success("🎉 Data Saved Successfully!")
                st.cache_data.clear()
            else:
                st.error("Please fill title and phone number.")

elif current_tab == "📋 Reports":
    st.subheader("📊 View Records")
    
    # Sub tabs for filtering records easily on mobile
    report_sub_tab = st.radio("Select View", ["Properties List", "Recent Visits"], horizontal=True)
    
    if report_sub_tab == "Properties List":
        props_data = supabase.table("inventory").select("*").order("created_at", descending=True).limit(20).execute().data
        if props_data:
            df = pd.DataFrame(props_data)[["title", "type", "price", "phone"]]
            # use_container_width ensures table scales perfectly inside phone screens
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No records found.")
            
    elif report_sub_tab == "Recent Visits":
        # Your visit logs
        st.info("Visits feature loading...")

elif current_tab == "🤝 Deals":
    st.subheader("🤝 Deals & Commission Registry")
    st.write("Track all financial entries here.")
    # Add your deals display or form here...
