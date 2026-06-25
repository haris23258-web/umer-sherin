import streamlit as st
from supabase import create_client
import pandas as pd
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
.report-box {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #0ea5e9;
    margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.action-card {
    background: white; padding: 15px; border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 12px;
    border: 1px solid #e2e8f0;
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

    st.markdown("---")
    st.subheader("📈 Staff Working & Progress Slide View")
    selected_staff = st.selectbox("🎯 Select Staff Member to View Progress Report:", list(USER_DB.keys()))
    
    col_report1, col_report2 = st.columns(2)
    with col_report1:
        st.markdown(f"📋 **Working Logs for: {selected_staff.title()}**")
        if logs:
            df_logs = pd.DataFrame(logs)
            if "target_area" in df_logs.columns and "user" in df_logs.columns:
                staff_filtered = df_logs[(df_logs["user"] == selected_staff) & (df_logs["target_area"] != "N/A")]
                if not staff_filtered.empty:
                    for idx, row in staff_filtered.head(5).iterrows():
                        st.markdown(f"""
                        <div class="report-box">
                            <span style="color:#0ea5e9; font-weight:bold; font-size:12px;">📍 AREA: {row['target_area']}</span>
                            <p style="margin:5px 0 0 0; font-size:14px; color:#1e293b;">{row['action']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else: st.info(f"{selected_staff.title()} ne abhi tak koi specific field area working record nahi ki.")
            else: st.info("Database attributes missing.")
        else: st.info("No logs available.")
        
    with col_report2:
        st.markdown(f"🏆 **Overall Leaderboard (Deals Count)**")
        if deals:
            df_deals = pd.DataFrame(deals)
            if "agent_name" in df_deals.columns:
                leaderboard = df_deals["agent_name"].value_counts().reset_index()
                leaderboard.columns = ["Staff Member", "Deals Completed Successfully"]
                st.dataframe(leaderboard, use_container_width=True, hide_index=True)
        else: st.info("Deals database empty.")

# -----------------------------
# QUICK ENTRY MODULE
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
                if not area or not owner_name or not owner_contact: st.warning("Please fill required fields.")
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
                if not client_name or not client_contact: st.warning("Please fill required fields.")
                else:
                    try:
                        supabase.table("clients").insert({
                            "client_name": client_name, "client_contact": client_contact,
                            "demand_type": demand_type, "max_budget": max_budget,
                            "preferred_area": preferred_area, "status": "Searching",
                            "last_interaction": "New registered client."
                        }).execute()
                        log_activity(st.session_state.user, f"Registered Client {client_name} for {preferred_area}", preferred_area)
                        st.success("Client registered successfully!")
                    except Exception as e: st.error(f"Error: {e}")

    with tab3:
        st.subheader("📝 Record Staff Field Working & Activity")
        with st.form("staff_work_form", clear_on_submit=True):
            cw1, cw2 = st.columns(2)
            if st.session_state.role == "Admin": working_staff = cw1.selectbox("Select Staff Member / Agent", list(USER_DB.keys()), key="ws_admin")
            else: working_staff = cw1.text_input("Staff Member", value=st.session_state.user, disabled=True, key="ws_agent")
            working_area = cw2.text_input("Target Area Name")
            activity_detail = st.text_area("What work was done today?")
            
            if st.form_submit_button("📢 Submit Progress Report"):
                if not working_area or not activity_detail: st.warning("All fields are required!")
                else:
                    log_activity(working_staff, activity_detail, working_area)
                    st.success("Progress report saved!")
                    st.rerun()

# -----------------------------
# 3. FIXED PROPERTIES MODULE WITH BUTTONS
# -----------------------------
elif st.session_state.current_nav == "Properties":
    st.title("🏡 Properties Master Database")
    search = st.text_input("🔍 Search Property by Area Name")
    
    try:
        properties = supabase.table("inventory").select("*").ilike("area", f"%{search}%").order("id", desc=True).execute().data
        if properties:
            for item in properties:
                # Layout card display with individual controls
                status_color = "#166534" if item["status"] in ["Rent Out", "Sold"] else "#1e3a8a"
                st.markdown(f"""
                <div class="action-card">
                    <span style="float:right; background:{status_color}; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:bold;">{item['status']}</span>
                    <h4 style="margin:0; color:#1e293b;">📍 {item['marla']} Marla - {item['area']} ({item['property_type']})</h4>
                    <p style="margin:5px 0; font-size:14px; color:#475569;">
                        <b>Price:</b> {item['price']:,} PKR | <b>Owner:</b> {item['owner_name']} ({item['owner_contact']}) | <b>Timing:</b> {item['visiting_time']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Action Button Rows
                b1, b2, _ = st.columns([1.5, 1.5, 7])
                if item["status"] not in ["Rent Out", "Sold"]:
                    if b1.button("✅ Mark Rent Out", key=f"rent_{item['id']}"):
                        supabase.table("inventory").update({"status": "Rent Out"}).eq("id", item["id"]).execute()
                        log_activity(st.session_state.user, f"Marked Property ID {item['id']} as Rent Out", item['area'])
                        st.success("Updated status!")
                        st.rerun()
                
                if b2.button("🚨 Delete Unit", key=f"del_prop_{item['id']}"):
                    supabase.table("inventory").delete().eq("id", item["id"]).execute()
                    log_activity(st.session_state.user, f"Deleted Property ID {item['id']}", item['area'])
                    st.warning("Property deleted.")
                    st.rerun()
                st.divider()
        else: st.info("No matching properties found.")
    except Exception as e: st.error(f"Error: {e}")

# -----------------------------
# 4. FIXED CLIENTS MODULE WITH ACTION & LAST TALK BUTTONS
# -----------------------------
elif st.session_state.current_nav == "Clients":
    st.title("👥 Registered Clients & Interactions Database")
    search_client = st.text_input("🔍 Search Client by Name")
    
    try:
        clients = supabase.table("clients").select("*").ilike("client_name", f"%{search_client}%").order("id", desc=True).execute().data
        if clients:
            for c in clients:
                status_tag_color = "#166534" if c["status"] == "House Found" else "#0ea5e9"
                last_talk = c.get("last_interaction", "Koi baat record nahi hui abhi tak.")
                
                st.markdown(f"""
                <div class="action-card" style="border-left: 5px solid {status_tag_color};">
                    <span style="float:right; background:{status_tag_color}; color:white; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:bold;">{c['status']}</span>
                    <h4 style="margin:0; color:#1e293b;">👤 Name: {c['client_name']} ({c['client_contact']})</h4>
                    <p style="margin:4px 0; font-size:14px; color:#475569;">
                        <b>Demand:</b> {c['demand_type']} | <b>Budget Max:</b> {c['max_budget']:,} PKR | <b>Preferred Area:</b> {c['preferred_area']}
                    </p>
                    <div style="background:#f1f5f9; padding:8px; border-radius:4px; margin-top:8px; font-size:13px; color:#334155;">
                        🗣️ <b>Last Time Kya Baat Hui Thi:</b> {last_talk}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Multi-Action Row for Client management
                col1, col2, col3 = st.columns([2, 2, 6])
                
                # Follow up Note update input field inline
                new_note = col3.text_input("Update Last Interaction Text Note:", key=f"note_val_{c['id']}", placeholder="Type latest conversation update...")
                if new_note:
                    if col3.button("💾 Save Talk Note", key=f"save_note_{c['id']}"):
                        supabase.table("clients").update({"last_interaction": new_note}).eq("id", c["id"]).execute()
                        st.success("Interaction note logged safely!")
                        st.rerun()

                if c["status"] != "House Found":
                    if col1.button("🤝 House Found", key=f"found_{c['id']}"):
                        supabase.table("clients").update({"status": "House Found"}).eq("id", c["id"]).execute()
                        log_activity(st.session_state.user, f"Marked Client {c['client_name']} as House Found", c['preferred_area'])
                        st.success("Status updated!")
                        st.rerun()
                        
                if col2.button("🚨 Delete Client", key=f"del_cli_{c['id']}"):
                    supabase.table("clients").delete().eq("id", c["id"]).execute()
                    log_activity(st.session_state.user, f"Deleted Client data for {c['client_name']}", c['preferred_area'])
                    st.warning("Client deleted.")
                    st.rerun()
                    
                st.divider()
        else: st.info("No registered clients match this name.")
    except Exception as e: st.error(f"Error: {e}")

# -----------------------------
# DEAL DONE REGISTRY MODULE
# -----------------------------
elif st.session_state.current_nav == "Deal Done Registry":
    st.title("🤝 Deal Closure & Done Registry")
    st.subheader("🎉 Record a New Successful Deal Entry")
    
    db_props, db_clients = [], []
    try:
        db_props = supabase.table("inventory").select("id, area, marla, price").neq("status", "Rent Out").execute().data
        db_clients = supabase.table("clients").select("id, client_name, preferred_area").neq("status", "House Found").execute().data
    except: pass

    with st.form("main_deal_done_entry_form", clear_on_submit=True):
        f_c1, f_c2 = st.columns(2)
        if db_props:
            prop_list = [f"ID: {p['id']} - {p['marla']} Marla at {p['area']} ({p['price']} PKR)" for p in db_props]
            selected_house = f_c1.selectbox("Select Property from Active Inventory:", prop_list)
        else: selected_house = f_c1.text_input("Ghar ki Detail / Manual Property Entry")
            
        if db_clients:
            client_list = [f"ID: {c['id']} - {c['client_name']} ({c['preferred_area']})" for c in db_clients]
            selected_client = f_c2.selectbox("Select Registered Client:", client_list)
        else: selected_client = f_c2.text_input("Client Name / Manual Client Entry")
            
        f_c3, f_c4 = st.columns(2)
        closing_agent = f_c3.selectbox("Which Staff Member closed this deal?", list(USER_DB.keys()))
        deal_commission = f_c4.number_input("Commission Earned (PKR)", min_value=0, value=20000, step=5000)
        deal_area = st.text_input("Deal Location / Area Name")

        if st.form_submit_button("🚀 Finalize and Lock This Deal"):
            if not selected_house or not selected_client: st.error("Details missing!")
            else:
                try:
                    final_house_str = str(selected_house)
                    final_client_str = str(selected_client)
                    
                    if "ID:" in final_house_str:
                        p_id = int(final_house_str.split("-")[0].replace("ID:", "").strip())
                        supabase.table("inventory").update({"status": "Rent Out"}).eq("id", p_id).execute()
                    if "ID:" in final_client_str:
                        c_id = int(final_client_str.split("-")[0].replace("ID:", "").strip())
                        supabase.table("clients").update({"status": "House Found"}).eq("id", c_id).execute()

                    supabase.table("deals").insert({
                        "client_name": final_client_str.split("-")[-1].strip() if "-" in final_client_str else final_client_str,
                        "property_details": final_house_str,
                        "agent_name": closing_agent,
                        "commission_earned": deal_commission
                    }).execute()
                    
                    log_activity(closing_agent, f"Successfully closed deal for {final_client_str} with {final_house_str}", deal_area if deal_area else "Closed Deal")
                    st.success("🔥 Deal Lock Ho Gayi!")
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")

# -----------------------------
# MATCHING, FINANCE & LOGS
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
    except: pass

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

elif st.session_state.current_nav == "Activity Logs":
    st.title("📋 Audit Activity Log System")
    if st.session_state.role != "Admin": st.error("Access denied.")
    else:
        try:
            logs = supabase.table("activity_logs").select("*").order("created_at", desc=True).execute().data
            if logs: st.dataframe(pd.DataFrame(logs)[["created_at", "user", "action", "target_area"]], use_container_width=True, hide_index=True)
        except: pass
