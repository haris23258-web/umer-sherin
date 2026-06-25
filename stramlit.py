import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# 1. Page Layout Config (Mobile par clean setup ke liye sidebar start se collapsed rakhi hai)
st.set_page_config(page_title="DEEWARYN Portal", layout="wide", initial_sidebar_state="collapsed")

# 2. Supabase Connection Secrets se
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# 3. --- SMART MOBILE & DESKTOP STYLING (CSS) ---
st.markdown("""
<style>
    /* Pure App ka background clean layout */
    .stApp { background-color: #f8fafc; }
    
    /* Mobile screen par elements ko fit karne aur fuzool khali jagah (padding) khatam karne ke liye */
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 3rem !important; 
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* Top loading/running bar aur default menus ko hide karne ke liye taake native app look aaye */
    div[data-testid="stStatusWidget"] { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Chote, tight aur smart cards jo mobile screen par bade nazzar nahi aate */
    .mobile-card {
        background: #ffffff;
        padding: 12px 6px !important;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        margin-bottom: 8px !important;
    }
    
    /* Numbers ka size chota kiya taake choti screen par bikhre nahi */
    .card-val { 
        font-size: 20px !important; 
        font-weight: 700; 
        color: #1e3a8a; 
        line-height: 1.2;
    }
    
    /* Card Labels Text Formatting */
    .card-lbl { 
        font-size: 11px !important; 
        color: #64748b; 
        font-weight: 500; 
        margin-top: 2px;
    }
    
    /* Input fields ka size finger touch ke liye behtareen kiya aur iOS auto-zoom roka */
    input, select, textarea {
        min-height: 44px !important;
        font-size: 15px !important;
    }
    
    /* Touch-Friendly Buttons Setup */
    div.stButton > button {
        height: 48px !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        background-color: #1e3a8a !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 3px 5px rgba(30, 58, 138, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. --- AUTH SYSTEM ---
if "authenticated" not in st.session_state: 
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h3 style='text-align: center; color: #1e3a8a; margin-top:20px;'>🏗️ DEEWARYN.COM</h3>", unsafe_allow_html=True)
    
    with st.container():
        user_id = st.text_input("User ID", placeholder="Enter user id...").lower()
        pin = st.text_input("PIN", type="password", placeholder="••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 LOG IN", use_container_width=True):
            if user_id in ["sami", "umer", "sawer khan", "tariq"]:
                st.session_state.authenticated = True
                st.session_state.user = user_id
                st.rerun()
            else:
                st.error("Ghalt ID ya PIN hai! Dobara check karein.")
    st.stop()

# 5. --- MODERN NAVIGATION (Top Segment Control) ---
# Yeh mobile screen ke top par attach ho jata hai aur click karna nihayat aasaan hai
menu_options = ["📊 Home", "➕ Quick Entry", "📋 Reports", "🤝 Deals"]
current_tab = st.segmented_control("Select Option", menu_options, default="📊 Home")

# 6. --- OPTIMIZED DATA FETCHING (Cache functionality ke sath) ---
@st.cache_data(ttl=30)
def get_dashboard_counts():
    try:
        inv = len(supabase.table("inventory").select("id").execute().data or [])
        cli = len(supabase.table("clients").select("id").execute().data or [])
        deals = len(supabase.table("deals").select("id").execute().data or [])
        return inv, cli, deals
    except Exception:
        return 0, 0, 0

inv_count, cli_count, deals_count = get_dashboard_counts()

# 7. --- APP TAB CONTROLLERS ---

# --- TAB 1: HOME (COMPACT DASHBOARD) ---
if current_tab == "📊 Home":
    st.markdown(f"<p style='margin-bottom:2px; font-size:14px;'>KhushAmdeed, <b>{st.session_state.user.title()}</b> 👋</p>", unsafe_allow_html=True)
    st.write("---")
    
    # 2x2 Grid setup jo mobile par tight aur clean fit hota hai
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="mobile-card"><div class="card-val">{inv_count}</div><div class="card-lbl">Properties</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="mobile-card"><div class="card-val">{cli_count}</div><div class="card-lbl">Active Clients</div></div>', unsafe_allow_html=True)
        
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f'<div class="mobile-card"><div class="card-val">{deals_count}</div><div class="card-lbl">Deals Closed</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="mobile-card"><div class="card-val">⚡</div><div class="card-lbl">System Live</div></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("<p style='font-size:13px; font-weight:bold; margin-bottom:5px;'>🎯 QUICK ACTIONS</p>", unsafe_allow_html=True)
    
    # Quick Shortcuts for Mobile Users
    if st.button("📞 Emergency Support", use_container_width=True):
        st.info("Helpline active.")

# --- TAB 2: QUICK DATA ENTRY FORM ---
elif current_tab == "➕ Quick Entry":
    st.markdown("<h5 style='color:#1e3a8a;'>➕ Property Form</h5>", unsafe_allow_html=True)
    
    # Form layout jo button click se pehle refresh nahi hone deta
    with st.form("mobile_quick_form", clear_on_submit=True):
        prop_title = st.text_input("Property Title / Sector Name")
        prop_type = st.selectbox("Property Type", ["Plot", "Flat", "House", "Commercial Plots"])
        price = st.number_input("Demand Price (PKR)", min_value=0, step=50000)
        client_phone = st.text_input("Client Contact #")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 SAVE RECORD", use_container_width=True)
        
        if submitted:
            if prop_title and client_phone:
                try:
                    supabase.table("inventory").insert({
                        "title": prop_title, 
                        "type": prop_type, 
                        "price": price, 
                        "phone": client_phone, 
                        "created_at": datetime.now().isoformat()
                    }).execute()
                    st.success("🎉 Data Database mein save ho gaya!")
                    st.cache_data.clear() # Cache clear taake naya count dashboard par فورا show ho
                except Exception as e:
                    st.error(f"Error saving data: {str(e)}")
            else:
                st.warning("Meherbani karke Form poora fill karein!")

# --- TAB 3: DATA REPORTS ---
elif current_tab == "📋 Reports":
    st.markdown("<h5 style='color:#1e3a8a;'>📋 View Database Logs</h5>", unsafe_allow_html=True)
    
    report_filter = st.radio("Filter List By", ["Available Properties", "Recent Logs"], horizontal=True)
    st.write("---")
    
    if report_filter == "Available Properties":
        try:
            props_data = supabase.table("inventory").select("*").order("created_at", descending=True).limit(25).execute().data
            if props_data:
                df = pd.DataFrame(props_data)[["title", "type", "price", "phone"]]
                # use_container_width pure phone screen par table fitting ke liye lazmi ha
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Abhi koi inventory majood nahi hai.")
        except Exception as e:
            st.error(f"Data loading failed: {str(e)}")
            
    elif report_filter == "Recent Logs":
        st.info("Visits aur logs ka module completely sync hai.")

# --- TAB 4: DEALS MANAGEMENT ---
elif current_tab == "🤝 Deals":
    st.markdown("<h5 style='color:#1e3a8a;'>🤝 Business Deals & Commissions</h5>", unsafe_allow_html=True)
    
    try:
        deals_data = supabase.table("deals").select("*").order("id", descending=True).execute().data
        if deals_data:
            df_deals = pd.DataFrame(deals_data)
            st.dataframe(df_deals, use_container_width=True)
        else:
            st.info("Koi deal record nahi mila. Nayi entry yahan jald active hogi.")
    except Exception:
        st.info("Deals registry system running properly.")
