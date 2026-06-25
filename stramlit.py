import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote
import re
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="EstateFlow Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CUSTOM CSS FOR HIGHLIGHTS & UI
# -----------------------------
st.markdown("""
<style>
.stApp { background-color: #f8fafc; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.kpi-card {
    background: white; padding: 20px; border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid #1e3a8a;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
try:
    supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# -----------------------------
# HELPERS
# -----------------------------
def clean_phone(phone):
    return re.sub(r"[^0-9]", "", str(phone)) if phone else ""

def log_activity(user, action, area="N/A"):
    try:
        supabase.table("activity_logs").insert({
            "user": user, 
            "action": action,
            "target_area": area
        }).execute()
    except:
        pass

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
USER_DB = {
    "sawer khan": {"role": "Admin", "pin": "sawer123"},
    "tariq": {"role": "Admin", "pin": "tariq456"},
    "agent": {"role": "Agent", "pin": "786"}
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔑 EstateFlow Pro Login")
    with st.container(border=True):
        user_id = st.text_input("User ID").lower().strip()
        user_pin = st.text_input("PIN", type="password")
        if st.button("Login", use_container_width=True):
            if user_id in USER_DB and USER_DB[user_id]["pin"] == user_pin:
                st.session_state.authenticated = True
                st.session_state.user = user_id
                st.session_state.role = USER_DB[user_id]["role"]
                st.rerun()
            else:
                st.error("Invalid login details")
    st.stop()

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Dashboard"

with st.sidebar:
    st.markdown("### 🏢 EstateFlow Pro")
    st.write(f"👤 **{st.session_state.user.title()}** ({st.session_state.role})")
    st.divider()
    
    modules = [
        {"name": "Dashboard", "icon": "📊"},
        {"name": "Quick Entry", "icon": "➕"},
        {"name": "Properties", "icon": "🏡"},
        {"name": "Clients", "icon": "👤"},
        {"name": "Deal Done Registry", "icon": "🤝"},
        {"name": "Deal Matcher", "icon": "🔍"},
        {"name": "Finance", "icon": "💰"},
        {"name": "Activity Logs", "icon": "📋"}
    ]
    
    for mod in modules:
        style_type = "primary" if st.session_state.current_nav == mod["name"] else "secondary"
        label = f"▶️ {mod['icon']} {mod['name']}" if st.session_state.current_nav == mod["name"] else f"{mod['icon']} {mod['name']}"
        if st.button(label, key=f"nav_{mod['name']}", use_container_width=True, type=style_type):
            st.session_state.current_nav = mod["name"]
            st.rerun()
            
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# -----------------------------
# 1. DASHBOARD MODULE
# -----------------------------
if st.session_state.current_nav == "Dashboard":
    st.title("📊 Portal Overview & Staff Analytics")
    
    inventory, clients_data, accounts, logs, deals = [], [], [], [], []
    try:
        inventory = supabase.table("inventory").select("*").execute().data
        clients_data = supabase.table("clients").select("*").execute().data
        accounts = supabase.table("accounts").select("*").execute().data
        logs = supabase.table("activity_logs").select("*").order("id", desc=True).execute().data
        deals = supabase.table("deals").select("*").execute().data
    except: pass

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="kpi-card"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">TOTAL PROPERTIES</p><h2 style="margin:5px 0 0 0;color:#1e3a8a;">{len(inventory) if inventory else 0} Units</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#0ea5e9;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">REGISTERED CLIENTS</p><h2 style="margin:5px 0 0 0;color:#0ea5e9;">{len(clients_data) if clients_data else 0} Active</h2></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#10b981;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">TOTAL DEALS CLOSED</p><h2 style="margin:5px 0 0 0;color:#10b981;">{len(deals) if deals else 0} Successful</h2></div>', unsafe_allow_html=True)

    # --- STAFF PROGRESS REPORT ---
    st.markdown("---")
    st.subheader("📈 Staff Working & Progress Report (Today's Analytics)")
    
    if logs or deals:
        col_report1, col_report2 = st.columns(2)
        
        with col_report1:
            st.markdown("🗣️ **Staff Field Working & Area Activity:**")
            if logs:
                df_logs = pd.DataFrame(logs)
                if "target_area" in df_logs.columns:
                    df_area_work = df_logs[df_logs["target_area"] != "N/A"][["user", "action", "target_area"]].head(10)
                    df_area_work.columns = ["Staff Member", "Activity / Detail", "Area Name"]
                    st.dataframe(df_area_work, use_container_width=True, hide_index=True)
                else:
                    st.info("No explicit field working recorded yet.")
            else: st.info("No activity logs.")
            
        with col_report2:
            st.markdown("🏆 **Leaderboard (Successful Deals by Agent):**")
            if deals:
                df_deals = pd.DataFrame(deals)
                if "agent_name" in df_deals.columns:
                    leaderboard = df_deals["agent_name"].value_counts().reset_index()
                    leaderboard.columns = ["Staff Member", "Deals Completed Successfully"]
                    st.dataframe(leaderboard, use_container_width=True, hide_index=True)
            else:
                st.info("No closed deals found in database ledger yet.")
    else:
        st.info("No activity or staff progress recorded today.")

    st.markdown("---")
    st.subheader("📌 Recent Listings Overview")
    if inventory:
        df_inv = pd.DataFrame(inventory)
        summary_cols = [c for c in ["id", "area", "marla", "property_type", "price", "status"] if c in df_inv.columns]
        def highlight_rented(row):
            return ['background-color: #dcfce7; color: #166534' if row.status in ['Rent Out', 'Sold'] else '' for _ in row]
        st.dataframe(df_inv[summary_cols].head(10).style.apply(highlight_rented, axis=1), use_container_width=True, hide_index=True)

# -----------------------------
# 2. QUICK ENTRY MODULE (FIXED WITH THIRD TAB FOR WORKING FORM)
# -----------------------------
elif st.session_state.current_nav == "Quick Entry":
    st.title("Quick Entry Wizard")
    tab1, tab2, tab3 = st.tabs([
        "🏡 House for Rent Entry", 
        "👤 Client Requirements Entry",
        "🗣️ Staff Daily Field Working Entry"
    ])

    with tab1:
        st.subheader("Add House for Rent")
        with st.form("quick_rent_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            area = c1.text_input("Area / Society Name")
            marla = c2.number_input("Size (Marla)", min_value=1.0, step=1.0)
            rent_price = c3.number_input("Monthly Rent Price (PKR)", min_value=0, step=1000)
            c4, c5, c6 = st.columns(3)
            category = c4.selectbox("Category", ["House", "Flat", "Portion", "Room"])
            status = c5.selectbox("Status", ["Available", "Rent Out", "Hold"])
            owner_name = c6.text_input("Owner Name")
            c7, c8 = st.columns(2)
            owner_contact = c7.text_input("Owner Contact Number")
            visiting_time = c8.text_input("Preferred Visiting Time")
            
            if st.form_submit_button("Save Property"):
                if not area or not owner_name or not owner_contact:
                    st.warning("Please fill required fields.")
                else:
                    try:
                        supabase.table("inventory").insert({
                            "area": area, "price": rent_price, "marla": marla,
                            "property_type": "Rent", "sub_type": category, "status": status,
                            "owner_name": owner_name, "owner_contact": owner_contact,
                            "visiting_time": visiting_time, "added_by": st.session_state.user
                        }).execute()
                        log_activity(st.session_state.user, f"Added {marla} Marla property in {area}", area)
                        st.success("Rent property saved safely!")
                    except Exception as e: st.error(f"Error: {e}")

    with tab2:
        st.subheader("Add Client Requirements")
        with st.form("quick_client_form", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            client_name = cc1.text_input("Client Name")
            client_contact = cc2.text_input("Client Contact")
            cc3, cc4 = st.columns(2)
            demand_type = cc3.selectbox("Demand Type", ["Rent", "Sale"])
            max_budget = cc4.number_input("Max Budget (PKR)", min_value=0, step=1000)
            preferred_area = st.text_input("Target Area")
            
            if st.form_submit_button("Register Client"):
                if not client_name or not client_contact:
                    st.warning("Please fill required fields.")
                else:
                    try:
                        supabase.table("clients").insert({
                            "client_name": client_name, "client_contact": client_contact,
                            "demand_type": demand_type, "max_budget": max_budget,
                            "preferred_area": preferred_area, "status": "Searching"
                        }).execute()
                        log_activity(st.session_state.user, f"Registered Client {client_name} for {preferred_area}", preferred_area)
                        st.success("Client registered successfully!")
                    except Exception as e: st.error(f"Error: {e}")

    # --- HEY BHAI! YEH RAHA NAYA STAFF WORKING FORM ---
    with tab3:
        st.subheader("📝 Record Staff Field Working & Activity")
        st.caption("Staff member rozana jis area mein visit karein ya jo bhi kaam karein, uski details yahan enter karein.")
        
        with st.form("staff_work_form", clear_on_submit=True):
            cw1, cw2 = st.columns(2)
            
            # Agar admin login hai toh kisi bhi staff ko select kar sakta hai, warna agent ka apna naam auto-select hoga
            if st.session_state.role == "Admin":
                working_staff = cw1.selectbox("Select Staff Member / Agent", list(USER_DB.keys()))
            else:
                working_staff = cw1.text_input("Staff Member", value=st.session_state.user, disabled=True)
                
            working_area = cw2.text_input("Target Area Name (e.g. DHA Phase 4, Bahria, G-11)")
            
            activity_detail = st.text_area("What work was done today? (Working Details)", 
                                           placeholder="e.g. Visited 3 houses with Client Asif, or Collected new house keys from owner, etc.")
            
            if st.form_submit_button("📢 Submit Progress Report"):
                if not working_area or not activity_detail:
                    st.warning("Area Name aur Working Details likhna zaroori hai!")
                else:
                    # Save working log straight to activity database
                    log_activity(working_staff, activity_detail, working_area)
                    st.success(f"Perfect! {working_staff} ki progress report area '{working_area}' ke liye save ho gayi hai aur dashboard par refresh ho chuki hai.")
                    
                    # Chota sa delay to let user see success, then rerun
                    st.rerun()

# -----------------------------
# PROPERTIES MODULE
# -----------------------------
elif st.session_state.current_nav == "Properties":
    st.title("🏡 Properties Master Database")
    search = st.text_input("🔍 Search Property by Area")
    try:
        properties = supabase.table("inventory").select("*").ilike("area", f"%{search}%").order("id", desc=True).execute().data
        if properties:
            df_inv = pd.DataFrame(properties)
            all_cols = ["id", "area", "marla", "property_type", "sub_type", "price", "status", "owner_name", "owner_contact"]
            display_cols = [c for c in all_cols if c in df_inv.columns]
            def style_prop_row(row):
                return ['background-color: #dcfce7; color: #166534; font-weight: bold;'] * len(row) if row.status in ["Rent Out", "Sold"] else [''] * len(row)
            st.dataframe(df_inv[display_cols].style.apply(style_prop_row, axis=1), use_container_width=True, hide_index=True)
        else: st.info("No properties found.")
    except Exception as e: st.error(f"Error: {e}")

# -----------------------------
# CLIENTS MODULE
# -----------------------------
elif st.session_state.current_nav == "Clients":
    st.title("👥 Registered Clients Database")
    search_client = st.text_input("🔍 Search Client by Name")
    try:
        clients = supabase.table("clients").select("*").ilike("client_name", f"%{search_client}%").order("id", desc=True).execute().data
        if clients:
            df_clients = pd.DataFrame(clients)
            all_client_cols = ["id", "client_name", "client_contact", "demand_type", "max_budget", "preferred_area", "status"]
            display_cols = [c for c in all_client_cols if c in df_clients.columns]
            def style_client_row(row):
                return ['background-color: #dcfce7; color: #166534; font-weight: bold;'] * len(row) if row.status == "House Found" else [''] * len(row)
            st.dataframe(df_clients[display_cols].style.apply(style_client_row, axis=1), use_container_width=True, hide_index=True)
        else: st.info("No client records found.")
    except Exception as e: st.error(f"Error: {e}")

# -----------------------------
# DEAL DONE REGISTRY
# -----------------------------
elif st.session_state.current_nav == "Deal Done Registry":
    st.title("🤝 Deal Closure & Done Registry")
    try:
        available_props = supabase.table("inventory").select("*").neq("status", "Rent Out").execute().data
        active_clients = supabase.table("clients").select("*").neq("status", "House Found").execute().data
        
        if not available_props or not active_clients:
            st.warning("Deals record karne ke liye system mein active clients aur available properties ka hona zaroori hai.")
        else:
            with st.form("deal_done_form", clear_on_submit=True):
                col_d1, col_d2 = st.columns(2)
                prop_options = {f"ID: {p['id']} - {p['marla']} Marla at {p['area']} ({p['price']} PKR)": p for p in available_props}
                client_options = {f"ID: {c['id']} - {c['client_name']} ({c['preferred_area']})": c for c in active_clients}
                
                selected_p_str = col_d1.selectbox("Select Finished Property", list(prop_options.keys()))
                selected_c_str = col_d2.selectbox("Select Matched Client", list(client_options.keys()))
                
                col_d3, col_d4 = st.columns(2)
                agent_involved = col_d3.selectbox("Which Staff Member closed the deal?", list(USER_DB.keys()))
                commission = col_d4.number_input("Commission Earned (PKR)", min_value=0, step=5000, value=15000)
                
                if st.form_submit_button("🎉 Lock and Confirm Deal Done"):
                    p_obj = prop_options[selected_p_str]
                    c_obj = client_options[selected_c_str]
                    
                    supabase.table("inventory").update({"status": "Rent Out"}).eq("id", p_obj["id"]).execute()
                    supabase.table("clients").update({"status": "House Found"}).eq("id", c_obj["id"]).execute()
                    supabase.table("deals").insert({
                        "client_name": c_obj["client_name"],
                        "property_details": f"{p_obj['marla']} Marla at {p_obj['area']}",
                        "agent_name": agent_involved,
                        "commission_earned": commission
                    }).execute()
                    
                    log_activity(agent_involved, f"Successfully Closed Deal for Client: {c_obj['client_name']}", p_obj['area'])
                    st.success(f"Mubarak ho! Deal done ho gayi hai.")
                    st.rerun()
    except Exception as e: st.error(f"Deal Registry Error: {e}")

# -----------------------------
# DEAL MATCHER MODULE
# -----------------------------
elif st.session_state.current_nav == "Deal Matcher":
    st.title("🔍 Matcher Deal Matching Engine")
    try:
        clients = supabase.table("clients").select("*").execute().data
        if clients:
            c_names = [x["client_name"] for x in clients]
            selected_c = st.selectbox("Choose Client Target", c_names)
            client_record = next((c for c in clients if c["client_name"] == selected_c), None)
            if client_record:
                budget = client_record.get("max_budget", 0)
                demand = client_record.get("demand_type")
                matched_data = supabase.table("inventory").select("*").eq("property_type", demand).lte("price", budget * 1.1).execute().data
                if matched_data:
                    for m in matched_data:
                        status_tag = '<span style="color:green; font-weight:bold;">Rent Out</span>' if m.get("status") == "Rent Out" else '<span style="color:blue; font-weight:bold;">Available</span>'
                        st.markdown(f"""
                        <div style="background:white; padding:15px; border-radius:8px; margin-bottom:10px; border:1px solid #ddd;">
                            <h4>📍 {m.get('area')} - {m.get('marla')} Marla ({status_tag})</h4>
                            <p>Demand Price: <b>{m.get('price'):,} PKR</b> | Client Budget Max: {budget:,} PKR</p>
                        </div>
                        """, unsafe_allow_html=True)
                else: st.warning("No matches available.")
    except Exception as e: st.error(f"Engine Exception: {e}")

# -----------------------------
# FINANCE MODULE
# -----------------------------
elif st.session_state.current_nav == "Finance":
    st.title("💰 Ledger Management")
    if st.session_state.role != "Admin": st.error("Restricted area.")
    else:
        with st.form("fin"):
            t = st.selectbox("Type", ["Income", "Expense"])
            amt = st.number_input("Amount", min_value=0)
            desc = st.text_area("Remarks")
            if st.form_submit_button("Save Ledger Row"):
                supabase.table("accounts").insert({"type": t, "amount": amt, "description": desc}).execute()
                st.success("Recorded.")
                st.rerun()

# -----------------------------
# ACTIVITY LOGS MODULE
# -----------------------------
elif st.session_state.current_nav == "Activity Logs":
    st.title("📋 Audit Activity Log System")
    if st.session_state.role != "Admin": st.error("Access denied.")
    else:
        try:
            logs = supabase.table("activity_logs").select("*").order("created_at", desc=True).execute().data
            if logs:
                st.dataframe(pd.DataFrame(logs)[["created_at", "user", "action", "target_area"]], use_container_width=True, hide_index=True)
        except: pass
