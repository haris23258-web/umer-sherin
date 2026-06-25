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
# CUSTOM CSS FOR HIGHLIGHTS & UI
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
# SIDEBAR NAVIGATION
# -----------------------------
if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Dashboard"

with st.sidebar:
    st.markdown("### 🏢 EstateFlow Pro")
    st.write(f"👤 **{st.session_state.user.title()}** ({st.session_state.role})")
    st.divider()
    
    st.markdown("**Navigation Menu**")
    modules = [
        {"name": "Dashboard", "icon": "📊"},
        {"name": "Quick Entry", "icon": "➕"},
        {"name": "Properties", "icon": "🏡"},
        {"name": "Clients", "icon": "👤"},
        {"name": "Deal Matcher", "icon": "🔍"},
        {"name": "Finance", "icon": "💰"},
        {"name": "Activity Logs", "icon": "📋"}
    ]
    
    for mod in modules:
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
        st.markdown(f'<div class="kpi-card"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">TOTAL PROPERTIES</p><h2 style="margin:5px 0 0 0;color:#1e3a8a;">{total_inventory} Units</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#0ea5e9;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">REGISTERED CLIENTS</p><h2 style="margin:5px 0 0 0;color:#0ea5e9;">{total_clients} Active</h2></div>', unsafe_allow_html=True)
    with m3:
        if st.session_state.role == "Admin":
            st.markdown(f'<div class="kpi-card" style="border-left-color:#10b981;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">TOTAL INCOME</p><h2 style="margin:5px 0 0 0;color:#10b981;">{int(total_revenue):,} PKR</h2></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-card" style="border-left-color:#94a3b8;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">ROLE STATUS</p><h2 style="margin:5px 0 0 0;color:#64748b;">Agent Mode</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📌 Recent Listings Overview")
    if inventory:
        df_inv = pd.DataFrame(inventory)
        summary_cols = [c for c in ["id", "area", "marla", "property_type", "price", "status"] if c in df_inv.columns]
        
        # Highlight Rent Out directly in Dataframe view
        def highlight_rented(row):
            return ['background-color: #dcfce7; color: #166534' if row.status in ['Rent Out', 'Sold'] else '' for _ in row]
            
        if "status" in df_inv.columns:
            st.dataframe(df_inv[summary_cols].head(10).style.apply(highlight_rented, axis=1), use_container_width=True, hide_index=True)
        else:
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
                            "required_marla": req_marla, "status": "Searching"
                        }).execute()
                        st.success("Client registered successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")

# -----------------------------
# PROPERTIES MODULE (WITH GREEN HIGHLIGHT FOR CLOSED DEALS)
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
            
            # Highlight closed deals (Rent Out / Sold) as light green row
            def style_prop_row(row):
                if row.status in ["Rent Out", "Sold"]:
                    return ['background-color: #dcfce7; color: #166534; font-weight: bold;'] * len(row)
                return [''] * len(row)
                
            st.dataframe(df_inv[display_cols].style.apply(style_prop_row, axis=1), use_container_width=True, hide_index=True)
            
            st.divider()
            st.subheader("🛠️ Property Quick Actions Registry")
            action_c1, action_c2, action_c3 = st.columns(3)
            
            prop_ids = [int(x["id"]) for x in properties]
            selected_id = action_c1.selectbox("Select Property ID to modify", prop_ids)
            selected_prop = next((p for p in properties if p["id"] == selected_id), None)
            
            if selected_prop:
                st.info(f"📍 Selected: {selected_prop['marla']} Marla ({selected_prop['status']}) at {selected_prop['area']}")
                
                if action_c2.button("🟢 Mark as 'Rent Out' / Sold", use_container_width=True):
                    supabase.table("inventory").update({"status": "Rent Out"}).eq("id", selected_id).execute()
                    supabase.table("activity_logs").insert({"user": st.session_state.user, "action": f"Marked Property #{selected_id} as Rent Out."}).execute()
                    st.success("Status updated to Rent Out!")
                    st.rerun()
                
                if st.session_state.role == "Admin":
                    if action_c3.button("🔴 Delete Property Record", use_container_width=True):
                        supabase.table("inventory").delete().eq("id", selected_id).execute()
                        st.warning("Property permanently removed.")
                        st.rerun()
        else:
            st.info("No properties found.")
    except Exception as e:
        st.error(f"Error: {e}")

# -----------------------------
# CLIENTS MODULE (UPDATED WITH HIGHLIGHT & ACTIONS)
# -----------------------------
elif st.session_state.current_nav == "Clients":
    st.title("👥 Registered Clients Database")
    search_client = st.text_input("🔍 Search Client by Name")
    
    try:
        clients = supabase.table("clients").select("*").ilike("client_name", f"%{search_client}%").order("id", desc=True).execute().data
        if clients:
            df_clients = pd.DataFrame(clients)
            
            # Pre-check columns
            if "status" not in df_clients.columns:
                df_clients["status"] = "Searching"
                
            all_client_cols = ["id", "client_name", "client_contact", "demand_type", "max_budget", "preferred_area", "required_marla", "status"]
            display_cols = [c for c in all_client_cols if c in df_clients.columns]
            
            # Highlight 'House Found' profiles as beautiful light green rows
            def style_client_row(row):
                if row.status == "House Found":
                    return ['background-color: #dcfce7; color: #166534; font-weight: bold;'] * len(row)
                return [''] * len(row)
                
            st.dataframe(df_clients[display_cols].style.apply(style_client_row, axis=1), use_container_width=True, hide_index=True)
            
            st.divider()
            
            # --- CLIENT QUICK ACTIONS ---
            st.subheader("🛠️ Client Actions Registry")
            cl_c1, cl_c2, cl_c3 = st.columns(3)
            
            client_ids = [int(x["id"]) for x in clients]
            selected_cl_id = cl_c1.selectbox("Select Client ID to modify", client_ids)
            selected_client_rec = next((c for c in clients if c["id"] == selected_cl_id), None)
            
            if selected_client_rec:
                current_cl_status = selected_client_rec.get('status', 'Searching')
                st.info(f"👤 Selected Client: **{selected_client_rec['client_name']}** (Current Status: **{current_cl_status}**)")
                
                # House Found Action Button
                if cl_c2.button("🎉 Mark as 'House Found'", use_container_width=True):
                    supabase.table("clients").update({"status": "House Found"}).eq("id", selected_cl_id).execute()
                    supabase.table("activity_logs").insert({
                        "user": st.session_state.user, "action": f"Marked Client #{selected_cl_id} status as House Found."
                    }).execute()
                    st.success(f"Client #{selected_cl_id} updated to House Found!")
                    st.rerun()
                    
                # Delete Client Action Button
                if st.session_state.role == "Admin":
                    if cl_c3.button("🔴 Delete Client Record", use_container_width=True):
                        supabase.table("clients").delete().eq("id", selected_cl_id).execute()
                        supabase.table("activity_logs").insert({
                            "user": st.session_state.user, "action": f"Deleted Client Record #{selected_cl_id}."
                        }).execute()
                        st.warning("Client record deleted successfully.")
                        st.rerun()
                else:
                    cl_c3.caption("🔒 *Delete restricted to Admin.*")
        else:
            st.info("No client records found.")
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
                        if m.get("status") == "Rent Out":
                            status_tag = '<span style="color:green; font-weight:bold;">Rent Out</span>'
                        else:
                            status_tag = '<span style="color:blue; font-weight:bold;">Available</span>'
                            
                        st.markdown(f"""
                        <div style="background:white; padding:15px; border-radius:8px; margin-bottom:10px; border:1px solid #ddd;">
                            <h4>📍 {m.get('area')} - {m.get('marla')} Marla ({status_tag})</h4>
                            <p>Demand Price: <b>{m.get('price'):,} PKR</b> | Client Budget Max: {budget:,} PKR</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        phone = clean_phone(client_record.get("client_contact"))
                        msg = quote(f"Salam {selected_c}, matching property found in {m.get('area')} for {m.get('price'):,} PKR.")
                        if phone:
                            st.link_button("💬 Send Update via WhatsApp", f"https://wa.me/{phone}?text={msg}", key=f"dm_{m['id']}")
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
