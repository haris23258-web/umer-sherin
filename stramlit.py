import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote
import re

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="EstateFlow Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CUSTOM CSS FOR SHARP PREMIUM UI
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #f8fafc;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border-left: 5px solid #1e3a8a;
    margin-bottom: 15px;
}
/* Custom styling for status color highlights in custom views */
.badge-green {
    background-color: #dcfce7;
    color: #166534;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: bold;
}
.badge-blue {
    background-color: #e0f2fe;
    color: #0369a1;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# -----------------------------
# HELPERS
# -----------------------------
def clean_phone(phone):
    return re.sub(r"[^0-9]", "", str(phone)) if phone else ""

def safe_value(val, default=""):
    return default if val is None else val

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
# 1. NEW SIDEBAR WITH PREMIUM BUTTON SHAPE MENU
# -----------------------------
if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Dashboard"

with st.sidebar:
    st.markdown("### 🏢 EstateFlow Pro")
    st.write(f"👤 **{st.session_state.user.title()}** ({st.session_state.role})")
    st.divider()
    
    st.markdown("**Navigation Menu**")
    
    # List of modules
    modules = [
        {"name": "Dashboard", "icon": "📊"},
        {"name": "Quick Entry", "icon": "➕"},
        {"name": "Properties", "icon": "🏡"},
        {"name": "Clients", "icon": "👤"},
        {"name": "Deal Matcher", "icon": "🔍"},
        {"name": "Finance", "icon": "💰"},
        {"name": "Activity Logs", "icon": "📋"}
    ]
    
    # Generating modern button-shaped options dynamically
    for mod in modules:
        # Highlight button if it's currently selected
        if st.session_state.current_nav == mod["name"]:
            button_label = f"▶️ {mod['icon']} {mod['name']}"
            type_style = "primary"
        else:
            button_label = f"{mod['icon']} {mod['name']}"
            type_style = "secondary"
            
        if st.button(button_label, key=f"nav_{mod['name']}", use_container_width=True, type=type_style):
            st.session_state.current_nav = mod["name"]
            st.rerun()
            
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# -----------------------------
# DASHBOARD MODULE
# -----------------------------
if st.session_state.current_nav == "Dashboard":
    st.title("📊 Portal Overview")
    
    # Data Fetching
    inventory, clients, accounts = [], [], []
    try:
        inventory = supabase.table("inventory").select("*").execute().data
        clients = supabase.table("clients").select("*").execute().data
        accounts = supabase.table("accounts").select("*").execute().data
    except Exception:
        pass

    total_inventory = len(inventory) if inventory else 0
    total_clients = len(clients) if clients else 0
    total_revenue = 0
    
    if accounts:
        df_acc = pd.DataFrame(accounts)
        if "type" in df_acc.columns and "amount" in df_acc.columns:
            total_revenue = df_acc[df_acc["type"] == "Income"]["amount"].sum()

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="kpi-card"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">TOTAL LISTINGS</p><h2 style="margin:5px 0 0 0;color:#1e3a8a;">{total_inventory} Units</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#0ea5e9;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">REGISTERED CLIENTS</p><h2 style="margin:5px 0 0 0;color:#0ea5e9;">{total_clients} Active</h2></div>', unsafe_allow_html=True)
    with m3:
        if st.session_state.role == "Admin":
            st.markdown(f'<div class="kpi-card" style="border-left-color:#10b981;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">TOTAL INCOME</p><h2 style="margin:5px 0 0 0;color:#10b981;">{int(total_revenue):,} PKR</h2></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-card" style="border-left-color:#94a3b8;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">ROLE STATUS</p><h2 style="margin:5px 0 0 0;color:#64748b;">Agent Mode</h2></div>', unsafe_allow_html=True)

    st.subheader("⚡ Navigation Shortcuts")
    q_col1, q_col2, q_col3 = st.columns(3)
    if q_col1.button("➕ Open Quick Entry Wizard", use_container_width=True, key="q1"):
        st.session_state.current_nav = "Quick Entry"
        st.rerun()
    if q_col2.button("🔍 Run Deal Matcher Engine", use_container_width=True, key="q2"):
        st.session_state.current_nav = "Deal Matcher"
        st.rerun()
    if q_col3.button("🏡 View Properties Table", use_container_width=True, key="q3"):
        st.session_state.current_nav = "Properties"
        st.rerun()

    st.markdown("---")
    st.subheader("📌 Recent Records Overview")
    if inventory:
        df_inv = pd.DataFrame(inventory)
        summary_cols = [c for c in ["id", "area", "marla", "property_type", "price", "status"] if c in df_inv.columns]
        st.dataframe(df_inv[summary_cols].head(10), use_container_width=True, hide_index=True)

# -----------------------------
# QUICK ENTRY MODULE
# -----------------------------
elif st.session_state.current_nav == "Quick Entry":
    st.title("Quick Entry Wizard")
    tab1, tab2 = st.tabs(["🏡 House for Rent Entry", "👤 Client Requirements Entry"])

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

            st.write("**⚙️ Available Utilities:**")
            u1, u2, u3 = st.columns(3)
            has_gas = u1.checkbox("Sui Gas Available")
            has_water = u2.checkbox("Water Supply")
            has_electricity = u3.checkbox("Electricity Meter")

            details = st.text_area("More Details")
            if st.form_submit_button("Save Property"):
                if not area or not owner_name or not owner_contact:
                    st.warning("Please fill required fields.")
                else:
                    try:
                        supabase.table("inventory").insert({
                            "area": area, "price": rent_price, "marla": marla,
                            "property_type": "Rent", "sub_type": category, "status": status,
                            "owner_name": owner_name, "owner_contact": owner_contact,
                            "visiting_time": visiting_time, "has_gas": has_gas,
                            "has_water": has_water, "has_electricity": has_electricity,
                            "details": details, "added_by": st.session_state.user
                        }).execute()
                        st.success("Rent property saved safely!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        st.subheader("Add Client Requirements")
        with st.form("quick_client_form", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            client_name = cc1.text_input("Client Name")
            client_contact = cc2.text_input("Client Contact")

            cc3, cc4 = st.columns(2)
            demand_type = cc3.selectbox("Demand Type", ["Rent", "Sale"])
            max_budget = cc4.number_input("Max Budget (PKR)", min_value=0, step=1000)

            cc5, cc6, cc7 = st.columns(3)
            req_beds = cc5.number_input("Required Bedrooms", min_value=1, value=2, step=1)
            preferred_area = cc6.text_input("Target Area")
            req_marla = cc7.number_input("Required Size (Marla)", min_value=1.0, step=1.0)

            if st.form_submit_button("Register Client"):
                if not client_name or not client_contact:
                    st.warning("Please fill required fields.")
                else:
                    try:
                        supabase.table("clients").insert({
                            "client_name": client_name, "client_contact": client_contact,
                            "demand_type": demand_type, "max_budget": max_budget,
                            "required_beds": int(req_beds), "preferred_area": preferred_area,
                            "required_marla": req_marla
                        }).execute()
                        st.success("Client registered successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")

# -----------------------------
# 2. PROPERTIES MODULE (UPDATED TO TABLE VIEW WITH ACTIONS)
# -----------------------------
elif st.session_state.current_nav == "Properties":
    st.title("🏡 Properties Master Database")
    st.caption("All properties displayed in a structural grid just like clients list.")

    search = st.text_input("🔍 Search Property by Area")

    try:
        properties = supabase.table("inventory").select("*").ilike("area", f"%{search}%").order("id", desc=True).execute().data
        
        if properties:
            df_inv = pd.DataFrame(properties)
            
            # Reorganizing columns beautifully
            all_cols = [
                "id", "area", "marla", "property_type", "sub_type", 
                "price", "status", "owner_name", "owner_contact", "visiting_time"
            ]
            display_cols = [c for c in all_cols if c in df_inv.columns]
            
            # --- COLOR RENDERING TRICK FOR STREAMLIT TABLE ---
            # Hum row style inject karne ke liye custom styling apply kar sakte hain table elements par
            st.dataframe(df_inv[display_cols], use_container_width=True, hide_index=True)
            
            st.divider()
            
            # --- ACTION OPERATIONS SECTION ---
            st.subheader("🛠️ Quick Actions Registry (Select ID from above table)")
            
            action_c1, action_c2, action_c3 = st.columns(3)
            
            prop_ids = [int(x["id"]) for x in properties]
            selected_id = action_c1.selectbox("Select Property ID to modify", prop_ids)
            
            # Fetch specific record to show current status
            selected_prop = next((p for p in properties if p["id"] == selected_id), None)
            
            if selected_prop:
                st.info(f"📍 Selected Property: **{selected_prop['marla']} Marla {selected_prop['sub_type']}** at **{selected_prop['area']}** (Current Status: **{selected_prop['status']}**)")
                
                # Rent Out Button/Option
                if action_c2.button("🟢 Mark as 'Rent Out' / Sold", use_container_width=True):
                    supabase.table("inventory").update({"status": "Rent Out"}).eq("id", selected_id).execute()
                    
                    supabase.table("activity_logs").insert({
                        "user": st.session_state.user, "action": f"Marked Property #{selected_id} as Rent Out."
                    }).execute()
                    st.success(f"Property #{selected_id} status updated successfully to Rent Out!")
                    st.rerun()
                
                # Delete Option
                if st.session_state.role == "Admin":
                    if action_c3.button("🔴 Delete Property Record", use_container_width=True):
                        supabase.table("inventory").delete().eq("id", selected_id).execute()
                        
                        supabase.table("activity_logs").insert({
                            "user": st.session_state.user, "action": f"Deleted Property Record #{selected_id}."
                        }).execute()
                        st.warning(f"Property #{selected_id} permanently removed from system.")
                        st.rerun()
                else:
                    action_c3.caption("🔒 *Delete option is restricted to Admin role.*")
                    
        else:
            st.info("No property listed yet.")
    except Exception as e:
        st.error(f"Failed to load records: {e}")

# -----------------------------
# CLIENTS MODULE
# -----------------------------
elif st.session_state.current_nav == "Clients":
    st.title("👥 Registered Clients Database")
    try:
        clients = supabase.table("clients").select("*").order("id", desc=True).execute().data
        if clients:
            df_clients = pd.DataFrame(clients)
            display_cols = [c for c in [
                "id", "client_name", "client_contact", "demand_type", 
                "max_budget", "preferred_area", "required_marla", "required_beds"
            ] if c in df_clients.columns]
            st.dataframe(df_clients[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No clients records found.")
    except Exception as e:
        st.error(f"Error: {e}")

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
                        score = 100
                        if m.get("status") == "Rent Out":
                            status_tag = '<span class="badge-green">Rent Out (Closed)</span>'
                        else:
                            status_tag = '<span class="badge-blue">Available</span>'
                            
                        st.markdown(f"""
                        <div style="background:white; padding:15px; border-radius:8px; margin-bottom:10px; border:1px solid #ddd;">
                            <h4>📍 {m.get('area')} - {m.get('marla')} Marla ({status_tag})</h4>
                            <p>Demand Price: <b>{m.get('price'):,} PKR</b> | Client Budget Max: {budget:,} PKR</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        phone = clean_phone(client_record.get("client_contact"))
                        msg = quote(f"Salam {selected_c}, matching property found in {m.get('area')} for {m.get('price'):,} PKR.")
                        if phone:
                            st.link_button("💬 Send Update", f"https://wa.me/{phone}?text={msg}", key=f"dm_{m['id']}")
                else:
                    st.warning("No matches available for this profile.")
    except Exception as e:
        st.error(f"Engine Exception: {e}")

# -----------------------------
# FINANCE MODULE
# -----------------------------
elif st.session_state.current_nav == "Finance":
    st.title("💰 Ledger Management")
    if st.session_state.role != "Admin":
        st.error("Restricted area.")
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
    if st.session_state.role != "Admin":
        st.error("Access denied.")
    else:
        try:
            logs = supabase.table("activity_logs").select("*").order("created_at", desc=True).execute().data
            if logs:
                st.dataframe(pd.DataFrame(logs)[["created_at", "user", "action"]], use_container_width=True, hide_index=True)
        except Exception:
            pass
