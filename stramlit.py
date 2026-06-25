import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# Page Layout
st.set_page_config(page_title="DEEWARYN Portal", layout="wide")

# --- UI STYLE (MOBILE RESPONSIVE) ---
st.markdown("""
<style>
    /* Mobile-first buttons */
    div.stButton > button { width: 100%; height: 50px; font-weight: bold; border-radius: 10px; }
    /* Beautiful Dashboard Cards */
    .metric-card { background: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .metric-value { font-size: 24px; font-weight: 800; color: #1e3a8a; }
    .metric-label { font-size: 12px; color: #64748b; text-transform: uppercase; margin-top: 5px; }
    /* Padding for Mobile */
    [data-testid="stSidebar"] { padding-top: 20px; }
</style>
""", unsafe_allow_html=True)

# Connection
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- AUTH ---
if "authenticated" not in st.session_state: st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🏗️ DEEWARYN.COM")
    st.image("mehfooz deewaryn logo WITH SLOGEN.png", width=250)
    user_id = st.text_input("User ID").lower()
    pin = st.text_input("PIN", type="password")
    if st.button("Login"):
        if user_id in ["sami", "umer", "sawer khan", "tariq"]:
            st.session_state.authenticated = True
            st.session_state.user = user_id
            st.rerun()
    st.stop()

# --- SIDEBAR (Mobile Friendly Navigation) ---
with st.sidebar:
    st.image("mehfooz deewaryn logo WITH SLOGEN.png", use_container_width=True)
    st.write(f"👤 **{st.session_state.user.title()}**")
    nav = st.radio("Menu", ["Dashboard", "Quick Entry", "Reports", "Deals", "Finance"])

# --- DASHBOARD (Rich Content) ---
if nav == "Dashboard":
    st.title("📊 Main Dashboard")
    
    # Data Fetch
    inv = supabase.table("inventory").select("id").execute().data
    cli = supabase.table("clients").select("id").execute().data
    deals = supabase.table("deals").select("id").execute().data
    
    # Grid for mobile/desktop
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(inv or [])}</div><div class="metric-label">Properties</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(cli or [])}</div><div class="metric-label">Clients</div></div>', unsafe_allow_html=True)
    
    st.write("")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(deals or [])}</div><div class="metric-label">Deals Done</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">📞</div><div class="metric-label">Support</div></div>', unsafe_allow_html=True)

    st.subheader("🚀 Quick Shortcuts")
    if st.button("➕ Add New Visit"): st.session_state.nav = "Quick Entry"; st.rerun()
    if st.button("📜 View Deals History"): st.session_state.nav = "Deals"; st.rerun()

elif nav == "Quick Entry":
    st.subheader("➕ Data Entry")
    # Yahan wohi form rakhein jo aapne pehle banaya tha (Mobile par yeh form automatically scrollable ban jata hai)
    # ... (Aap apna purana Quick Entry ka code yahan paste karein) ...

elif nav == "Reports":
    st.title("📋 Database Reports")
    # Tabs for better mobile use
    tab1, tab2 = st.tabs(["Properties", "Visits"])
    with tab1:
        props = supabase.table("inventory").select("*").execute().data
        st.dataframe(pd.DataFrame(props), use_container_width=True)
    with tab2:
        visits = supabase.table("property_visits").select("*").execute().data
        st.dataframe(pd.DataFrame(visits), use_container_width=True)

elif nav == "Deals":
    st.title("🤝 Deals Registry")
    # ... (Aap apna purana Deals ka code yahan paste karein) ...
