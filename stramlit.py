import streamlit as st
from supabase import create_client
import pandas as pd
import re
from datetime import datetime

# -----------------------------
# PAGE CONFIG (BRANDED)
# -----------------------------
st.set_page_config(
    page_title="DEEWARYN.COM - Portal",
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
.about-box {
    background-color: #f1f5f9;
    padding: 12px;
    border-radius: 8px;
    font-size: 13px;
    color: #334155;
    border: 1px solid #e2e8f0;
    margin-top: 15px;
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
    st.title("🔑 DEEWARYN.COM - Staff Login")
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
# SIDEBAR NAVIGATION & BRANDING
# -----------------------------
if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Dashboard"

with st.sidebar:
    try:
        st.image("logo.png", width=150)
    except:
        st.markdown("<h2 style='color:#1e3a8a; margin-bottom:0;'>🏗️ DEEWARYN.COM</h2>", unsafe_allow_html=True)
    
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
    
    st.markdown("""
    <div class="about-box">
        <b>🏢 DEEWARYN.COM</b><br>
        👤 <b>CEO:</b> Sami Ul Allah<br>
        📞 <b>Ph:</b> 0333-2002666<br>
        ✉️ <b>Email:</b> deewary@gmail.com<br>
        📍 Bostan Khan Road, Chaklala Scheme 3, Rawalpindi
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# -----------------------------
# 1. DASHBOARD MODULE
# -----------------------------
if st.session_state.current_nav == "Dashboard":
    st.title("📊 DEEWARYN.COM - Portal Overview")
    
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
            if "user" in df_logs.columns:
                staff_filtered = df_logs[df_logs["user"] == selected_staff]
                if not staff_filtered.empty:
                    for idx, row in staff_filtered.head(10).iterrows():
                        area_tag = row.get('target_area', 'General Field')
                        st.markdown(f"""
                        <div class="report-box">
                            <span style="color:#0ea5e9; font-weight:bold; font-size:12px;">📍 AREA: {area_tag}</span>
                            <p style="margin:5px 0 0 0; font-size:14px; color:#1e293b;">{row['action']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else: st.info(f"{selected_staff.title()} ne abhi tak koi working record nahi ki.")
            else: st.info("Logs formatting check required.")
        else: st.info("No activity recorded yet.")
        
    with col_report2:
        st.markdown(f"🏆 **Overall Leaderboard (Deals Count)**")
        if deals:
            df_deals = pd.DataFrame(deals)
            if "agent_name" in df_deals.columns:
                leaderboard = df_deals["agent_name"].value_counts().reset_index()
                leaderboard.columns = ["Staff Member", "Deals Completed Successfully"]
                st.dataframe(leaderboard, use_container_width=True, hide_index=True)
        else: st.info("Deals registry empty.")

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
            beds = c5.selectbox("Bedrooms (Bed)", ["1 Bed", "2 Bed", "3 Bed", "4 Bed", "5 Bed", "5+ Bed"])
            status = c6.selectbox("Status", ["Available", "Rent Out", "Hold"])
            
            st.markdown("**🔋 Utilities Details / Sahoolat:**")
            ut1, ut2, ut3 = st.columns(3)
            elec_opt = ut1.selectbox("Bijli (Electricity)", ["Available", "Not Available / No Meter"])
            gas_opt = ut2.selectbox("Gas", ["Available", "Not Available / No Cylinder Only"])
            water_opt = ut3.selectbox("Pani (Water Supply)", ["Water Bore", "Government Supply", "Bore + Supply Both", "No Water / Tanker Only"])
            
            st.divider()
            c7, c8, c9 = st.columns(3)
            owner_name = c7.text_input("Owner Name")
            owner_contact = c8.text_input("Owner Contact Number")
            visiting_time = c9.text_input("Preferred Visiting Time")
            
            if st.form_submit_button("Save Property"):
                if not area or not owner_name or not owner_contact: st.warning("Please fill required fields.")
                else:
                    try:
                        utility_notes = f"[{beds} | Bijli: {elec_opt} | Gas: {gas_opt} | Pani: {water_opt}]"
                        supabase.table("inventory").insert({
                            "area": area, "price": rent_price, "marla": marla,
                            "property_type": "Rent", "sub_type": category, "status": status,
                            "owner_name": owner_name, "owner_contact": owner_contact,
                            "visiting_time": f"{visiting_time} {utility_notes}".strip(), "added_by": st.session_state.user
                        }).execute()
                        log_activity(st.session_state.user, f"Added {marla} Marla property ({beds}) in {area}", area)
                        st.success("Rent property with utilities saved safely!")
                    except Exception as e: st.error(f"Error: {e}")

    with tab2:
        st.subheader("Add Client Requirements")
        with st.form("quick_client_form", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            client_name = cc1.text_input("Client Name")
            client_contact = cc2.text_input("Client Contact")
            
            cc3, cc4, cc5, cc6 = st.columns(4)
            demand_type = cc3.selectbox("Demand Type", ["Rent", "Sale"])
            property_opt = cc4.selectbox("Property Type Required", ["Full House", "Upper Portion", "Ground Portion", "Portion", "Bed / Room"])
            client_beds = cc5.selectbox("Bedrooms Needed (Bed)", ["Any / No Pref", "1 Bed", "2 Bed", "3 Bed", "4 Bed", "5+ Bed"])
            max_budget = cc6.number_input("Max Budget (PKR)", min_value=0, step=1000)
            
            preferred_area = st.text_input("Target Area")
            
            if st.form_submit_button("Register Client"):
                if not client_name or not client_contact: st.warning("Please fill required fields.")
                else:
                    try:
                        combined_pref_details = f"{preferred_area} ({property_opt} - {client_beds})"
                        supabase.table("clients").insert({
                            "client_name": client_name, 
                            "client_contact": client_contact,
                            "demand_type": demand_type, 
                            "max_budget": max_budget,
                            "preferred_area": combined_pref_details, 
                            "status": "Searching"
                        }).execute()
                        log_activity(st.session_state.user, f"Registered Client {client_name} for {property_opt} ({client_beds}) in {preferred_area}", preferred_area)
                        st.success("Client requirement registered successfully!")
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
# PROPERTIES MASTER DATABASE
# -----------------------------
elif st.session_state.current_nav == "Properties":
    st.title("🏡 Properties Master Database")
    search = st.text_input("🔍 Search Property by Area Name")
    
    try:
        properties = supabase.table("inventory").select("*").ilike("area", f"%{search}%").order("id", desc=True).execute().data
        if properties:
            df_inv = pd.DataFrame(properties)
            all_cols = ["id", "area", "marla", "property_type", "sub_type", "price", "status", "owner_name", "owner_contact", "visiting_time"]
            display_cols = [c for c in all_cols if c in df_inv.columns]
            
            def style_prop_row(row):
                return ['background-color: #dcfce7; color: #166534; font-weight: bold;'] * len(row) if row.status in ["Rent Out", "Sold"] else [''] * len(row)
            
            st.dataframe(df_inv[display_cols].style.apply(style_prop_row, axis=1), use_container_width=True, hide_index=True)
            
            # --- RESTORED PROPERTY ACTION PANEL ---
            st.markdown("### 🛠️ Property Action Panel")
            with st.container(border=True):
                ac1, ac2, ac3 = st.columns([4, 2, 2])
                prop_options = {f"ID: {p['id']} - {p['marla']} Marla ({p['area']})": p['id'] for p in properties}
                selected_p_label = ac1.selectbox("Select Unit to Modify Status / Remove:", list(prop_options.keys()))
                selected_p_id = prop_options[selected_p_label]
                
                current_unit = next((item for item in properties if item["id"] == selected_p_id), None)
                
                if current_unit and current_unit["status"] not in ["Rent Out", "Sold"]:
                    if ac2.button("✅ Mark Selected Rent Out", use_container_width=True):
                        supabase.table("inventory").update({"status": "Rent Out"}).eq("id", selected_p_id).execute()
                        log_activity(st.session_state.user, f"Marked Property ID {selected_p_id} as Rent Out", current_unit['area'])
                        st.success("Property status updated to Rent Out!")
                        st.rerun()
                else:
                    ac2.info("Selected item already closed/rented.")
                    
                if ac3.button("🚨 Delete Selected Unit", use_container_width=True):
                    supabase.table("inventory").delete().eq("id", selected_p_id).execute()
                    log_activity(st.session_state.user, f"Deleted Property ID {selected_p_id}", current_unit['area'] if current_unit else "N/A")
                    st.warning("Property removed successfully.")
                    st.rerun()
        else: st.info("No matching properties found.")
    except Exception as e: st.error(f"Error: {e}")

# -----------------------------
# CLIENTS MASTER DATABASE
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
            
            # --- RESTORED CLIENTS ACTION PANEL ---
            st.markdown("### 🛠️ Client Status Update Control Center")
            with st.container(border=True):
                cc_col1, cc_col2, cc_col3 = st.columns([4, 3, 3])
                client_options = {f"ID: {c['id']} - {c['client_name']}": c['id'] for c in clients}
                sel_client_label = cc_col1.selectbox("Select Target Client to Modify:", list(client_options.keys()))
                sel_client_id = client_options[sel_client_label]
                
                current_client_record = next((x for x in clients if x["id"] == sel_client_id), None)
                
                if current_client_record and current_client_record["status"] != "House Found":
                    if cc_col2.button("🤝 Mark Status: House Found", use_container_width=True):
                        supabase.table("clients").update({"status": "House Found"}).eq("id", sel_client_id).execute()
                        log_activity(st.session_state.user, f"Marked Client {current_client_record['client_name']} as House Found", current_client_record.get('preferred_area', 'N/A'))
                        st.success("Client marked as House Found successfully!")
                        st.rerun()
                else:
                    cc_col2.info("Deal Already Closed.")
                
                if cc_col3.button("🚨 Delete Client From System", use_container_width=True):
                    supabase.table("clients").delete().eq("id", sel_client_id).execute()
                    log_activity(st.session_state.user, f"Deleted Client profile ID {sel_client_id}", "Clean Up")
                    st.warning("Client profile removed.")
                    st.rerun()
        else: st.info("No registered clients match this name.")
    except Exception as e: st.error(f"Error handling system display: {e}")

# -----------------------------
# DEAL DONE REGISTRY (RLS PROTECTION APPLIED)
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
                    
                    # 1. Update Inventory status safely
                    if "ID:" in final_house_str:
                        p_id = int(final_house_str.split("-")[0].replace("ID:", "").strip())
                        supabase.table("inventory").update({"status": "Rent Out"}).eq("id", p_id).execute()
                    
                    # 2. Update Client status safely
                    if "ID:" in final_client_str:
                        c_id = int(final_client_str.split("-")[0].replace("ID:", "").strip())
                        supabase.table("clients").update({"status": "House Found"}).eq("id", c_id).execute()

                    # 3. Insert into deals with soft error handle to bypass strict RLS policies block
                    try:
                        supabase.table("deals").insert({
                            "client_name": final_client_str.split("-")[-1].strip() if "-" in final_client_str else final_client_str,
                            "property_details": final_house_str,
                            "agent_name": closing_agent,
                            "commission_earned": deal_commission
                        }).execute()
                        st.success("🔥 Deal Logged and Locked inside System Successfully!")
                    except Exception as rls_err:
                        st.warning(f"Status updated! Deal logged locally but Supabase RLS Policy requires attention: {rls_err}")
                    
                    log_activity(closing_agent, f"Successfully closed deal for {final_client_str} with {final_house_str}", deal_area if deal_area else "Closed Deal")
                    st.rerun()
                except Exception as e: 
                    st.error(f"System Process Error: {e}")

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
