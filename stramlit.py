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
# CUSTOM CSS FOR PROFESSIONAL LOOK
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
.main-card {
    background: white;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    margin-bottom: 20px;
    border: 1px solid #e2e8f0;
}
.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border-left: 5px solid #1e3a8a;
    margin-bottom: 15px;
}
.small-title {
    font-size: 18px;
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 10px;
}
.status-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 50px;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}
.available { background: #dcfce7; color: #166534; }
.hold { background: #fef3c7; color: #92400e; }
.sold { background: #fee2e2; color: #991b1b; }

/* Utilities tag style */
.utility-tag {
    display: inline-block;
    background: #f1f5f9;
    color: #475569;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 12px;
    margin-right: 5px;
    font-weight: 600;
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

def status_class(status):
    if status == "Available": return "available"
    if status == "Sold": return "sold"
    return "hold"

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
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.title("🏢 EstateFlow Pro")
    st.write(f"**Welcome:** {st.session_state.user.title()}")
    st.caption(f"Role: {st.session_state.role}")
    st.divider()

    # Session state variable to handle navigation smoothly via quick links too
    if "current_nav" not in st.session_state:
        st.session_state.current_nav = "Dashboard"

    nav = st.radio("Select Module", [
        "Dashboard", "Quick Entry", "Properties", 
        "Clients", "Deal Matcher", "Finance", "Activity Logs"
    ], index=["Dashboard", "Quick Entry", "Properties", "Clients", "Deal Matcher", "Finance", "Activity Logs"].index(st.session_state.current_nav))
    
    st.session_state.current_nav = nav
    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# -----------------------------
# 1. NEW DASHBOARD (REAL WEBSITE LOOK)
# -----------------------------
if st.session_state.current_nav == "Dashboard":
    st.title("📊 Portal Overview")
    st.caption("Real-time estate metrics and quick controls.")

    # Data Loading
    inventory = []
    clients = []
    accounts = []
    try:
        inventory = supabase.table("inventory").select("*").execute().data
        clients = supabase.table("clients").select("*").execute().data
        accounts = supabase.table("accounts").select("*").execute().data
    except Exception as e:
        pass

    total_inventory = len(inventory) if inventory else 0
    total_clients = len(clients) if clients else 0
    total_revenue = 0
    
    if accounts:
        df_acc = pd.DataFrame(accounts)
        if "type" in df_acc.columns and "amount" in df_acc.columns:
            total_revenue = df_acc[df_acc["type"] == "Income"]["amount"].sum()

    # Professional KPI Layout
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="kpi-card"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">ACTIVE INVENTORY</p><h2 style="margin:5px 0 0 0;color:#1e3a8a;">{total_inventory} Properties</h2></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="kpi-card" style="border-left-color:#0ea5e9;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">TOTAL CLIENTS</p><h2 style="margin:5px 0 0 0;color:#0ea5e9;">{total_clients} Registered</h2></div>', unsafe_allow_html=True)
    with m3:
        if st.session_state.role == "Admin":
            st.markdown(f'<div class="kpi-card" style="border-left-color:#10b981;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">TOTAL REVENUE</p><h2 style="margin:5px 0 0 0;color:#10b981;">{int(total_revenue):,} PKR</h2></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="kpi-card" style="border-left-color:#94a3b8;"><p style="margin:0;color:#64748b;font-size:14px;font-weight:600;">ACCESS LEVEL</p><h2 style="margin:5px 0 0 0;color:#64748b;">Agent Mode</h2></div>', unsafe_allow_html=True)

    # Quick Action Hub (Just like a premium dashboard)
    st.subheader("⚡ Quick Actions")
    q_col1, q_col2, q_col3 = st.columns(3)
    if q_col1.button("➕ Add New Rent House / Client", use_container_width=True):
        st.session_state.current_nav = "Quick Entry"
        st.rerun()
    if q_col2.button("🔍 Open Deal Matcher Engine", use_container_width=True):
        st.session_state.current_nav = "Deal Matcher"
        st.rerun()
    if q_col3.button("📂 View All Properties List", use_container_width=True):
        st.session_state.current_nav = "Properties"
        st.rerun()

    st.markdown("---")
    
    # Recent Listings Table instead of old graphs
    st.subheader("📌 Recent Listings Summary")
    if inventory:
        df_inv = pd.DataFrame(inventory)
        summary_cols = [c for c in ["id", "area", "marla", "property_type", "sub_type", "price", "status"] if c in df_inv.columns]
        st.dataframe(df_inv[summary_cols].head(10), use_container_width=True, hide_index=True)
    else:
        st.info("No recent data available to display.")

# -----------------------------
# 2. QUICK ENTRY (UPDATED WITH UTILITIES & CLIENT FILTERS)
# -----------------------------
elif st.session_state.current_nav == "Quick Entry":
    st.title("Quick Entry Wizard")
    tab1, tab2 = st.tabs(["🏡 House for Rent Entry", "👤 Client Requirements Entry"])

    # HOUSE FOR RENT
    with tab1:
        st.subheader("Add House for Rent with Utilities")
        with st.form("quick_rent_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            area = c1.text_input("Area / Society Name")
            marla = c2.number_input("Size (Marla)", min_value=1.0, step=1.0)
            rent_price = c3.number_input("Monthly Rent Price (PKR)", min_value=0, step=1000)

            c4, c5, c6 = st.columns(3)
            category = c4.selectbox("Category", ["House", "Flat", "Portion", "Room"])
            status = c5.selectbox("Status", ["Available", "Hold"])
            owner_name = c6.text_input("Owner Name")

            c7, c8 = st.columns(2)
            owner_contact = c7.text_input("Owner Contact Number")
            visiting_time = c8.text_input("Preferred Visiting Time (e.g., 4PM to 7PM)")

            # Nayi Changes: Gas, Paani, Bijli Options
            st.write("**⚙️ Available Utilities:**")
            u1, u2, u3 = st.columns(3)
            has_gas = u1.checkbox("Sui Gas Available")
            has_water = u2.checkbox("Water Supply / Bore Available")
            has_electricity = u3.checkbox("Electricity Meter Installed")

            details = st.text_area("More Details / Hidden Features")

            save_rent = st.form_submit_button("Save Property to Live Portal")

            if save_rent:
                if not area or not owner_name or not owner_contact:
                    st.warning("Please fill required fields (Area, Owner Name, Contact).")
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

                        supabase.table("activity_logs").insert({
                            "user": st.session_state.user,
                            "action": f"Added rent property in {area} with utilities configuration."
                        }).execute()
                        st.success("Rent property with detailed utilities added successfully!")
                    except Exception as e:
                        st.error(f"Failed to save property: {e}")

    # CLIENT ENTRY (WITH BED, AREA, MARLA FILTERS)
    with tab2:
        st.subheader("Add Client Demands & Filters")
        with st.form("quick_client_form", clear_on_submit=True):
            cc1, cc2 = st.columns(2)
            client_name = cc1.text_input("Client Name")
            client_contact = cc2.text_input("Client Contact")

            cc3, cc4 = st.columns(2)
            demand_type = cc3.selectbox("Demand Type", ["Rent", "Sale"])
            max_budget = cc4.number_input("Max Budget (PKR)", min_value=0, step=1000)

            # Nayi Changes: Beds, Preferred Area, Marla
            st.write("**🎯 Specific Requirements:**")
            cc5, cc6, cc7 = st.columns(3)
            req_beds = cc5.number_input("Required Bedrooms", min_value=1, max_value=20, value=2, step=1)
            preferred_area = cc6.text_input("Target Area / Sector")
            req_marla = cc7.number_input("Required Size (Marla)", min_value=1.0, step=1.0)

            save_client = st.form_submit_button("Register Client Demand")

            if save_client:
                if not client_name or not client_contact:
                    st.warning("Please fill Client Name and Contact Number.")
                else:
                    try:
                        supabase.table("clients").insert({
                            "client_name": client_name, "client_contact": client_contact,
                            "demand_type": demand_type, "max_budget": max_budget,
                            "required_beds": int(req_beds), "preferred_area": preferred_area,
                            "required_marla": req_marla
                        }).execute()

                        supabase.table("activity_logs").insert({
                            "user": st.session_state.user,
                            "action": f"Registered client {client_name} looking for {req_marla} Marla in {preferred_area}."
                        }).execute()
                        st.success("Client registered with custom tags successfully!")
                    except Exception as e:
                        st.error(f"Failed to save client details: {e}")

# -----------------------------
# 3. PROPERTIES (DISPLAY DETAILED UTILITIES)
# -----------------------------
elif st.session_state.current_nav == "Properties":
    st.title("All Live Properties")
    search = st.text_input("🔍 Filter Listings by Area Name")

    try:
        properties = supabase.table("inventory").select("*").ilike("area", f"%{search}%").order("id", desc=True).execute().data
        if properties:
            for p in properties:
                s = safe_value(p.get("status"))
                s_class = status_class(s)

                # Generating Utility badges dynamically
                gas_badge = '<span class="utility-tag">🔥 Gas</span>' if p.get("has_gas") else ''
                water_badge = '<span class="utility-tag">💧 Water</span>' if p.get("has_water") else ''
                elec_badge = '<span class="utility-tag">⚡ Electricity</span>' if p.get("has_electricity") else ''
                
                st.markdown(f"""
                <div class="main-card">
                    <span class="status-badge {s_class}">{s}</span>
                    <div class="small-title" style="margin-top:10px;">📍 {safe_value(p.get("area"))}</div>
                    <p style="margin:4px 0;"><b>{safe_value(p.get("marla"))} Marla {safe_value(p.get("sub_type"))} ({safe_value(p.get("property_type"))})</b></p>
                    <p style="margin:4px 0; color:#16a34a; font-size:16px;">Price: <b>{safe_value(p.get("price"), 0):,} PKR</b></p>
                    <div style="margin:10px 0;">{gas_badge}{water_badge}{elec_badge}</div>
                    <p style="margin:4px 0; font-size:13px; color:#64748b;"><b>⏰ Timing:</b> {safe_value(p.get("visiting_time"), "Not Specified")} | <b>📝 Details:</b> {safe_value(p.get("details"), "None")}</p>
                    <p style="margin:4px 0; font-size:13px; color:#475569;">👤 Owner: {safe_value(p.get("owner_name"))} - {safe_value(p.get("owner_contact"))}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.role == "Admin" and p.get("status") == "Available" and p.get("id"):
                    if st.button(f"Mark as Sold #{p['id']}", key=f"sold_{p['id']}"):
                        supabase.table("inventory").update({"status": "Sold"}).eq("id", p["id"]).execute()
                        st.rerun()
        else:
            st.info("No matched property found in database.")
    except Exception as e:
        st.error(f"Failed to load: {e}")

# -----------------------------
# 4. CLIENTS LIST (DISPLAY EXTENDED FILTERS)
# -----------------------------
elif st.session_state.current_nav == "Clients":
    st.title("Registered Clients Database")
    try:
        clients = supabase.table("clients").select("*").order("id", desc=True).execute().data
        if clients:
            df_clients = pd.DataFrame(clients)
            # Reordering columns to show newly added demand filters upfront
            display_cols = [c for c in [
                "id", "client_name", "client_contact", "demand_type", 
                "max_budget", "preferred_area", "required_marla", "required_beds"
            ] if c in df_clients.columns]
            st.dataframe(df_clients[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No clients found.")
    except Exception as e:
        st.error(f"Failed: {e}")

# -----------------------------
# 5. DEAL MATCHER
# -----------------------------
elif st.session_state.current_nav == "Deal Matcher":
    st.title("Smart AI Deal Matcher")
    try:
        clients = supabase.table("clients").select("*").execute().data
    except Exception as e:
        st.stop()

    if clients:
        client_names = [c["client_name"] for c in clients if "client_name" in c]
        if client_names:
            selected_client = st.selectbox("Choose Client Profile", client_names)
            client = next((x for x in clients if x.get("client_name") == selected_client), None)

            if client:
                demand_type = client.get("demand_type")
                budget = client.get("max_budget", 0)
                pref_area = client.get("preferred_area")

                try:
                    # Initial query matching basics
                    query = supabase.table("inventory").select("*").eq("property_type", demand_type).lte("price", budget * 1.1).eq("status", "Available")
                    matched = query.execute().data

                    if matched:
                        for m in matched:
                            score = 100
                            # Deduct points if criteria misses
                            if m.get("price", 0) > budget: score -= 15
                            if pref_area and pref_area.lower() not in safe_value(m.get("area")).lower(): score -= 20

                            # Dynamic badging
                            g_tag = '🔥 Gas ' if m.get("has_gas") else ''
                            w_tag = '💧 Water ' if m.get("has_water") else ''
                            e_tag = '⚡ Elec' if m.get("has_electricity") else ''

                            st.markdown(f"""
                            <div class="main-card" style="border-left: 6px solid #10b981;">
                                <div class="small-title">Match Score: {score}%</div>
                                <p style="margin:2px 0;">📍 Location: <b>{safe_value(m.get("area"))}</b></p>
                                <p style="margin:2px 0;">Price Tag: <b style="color:#16a34a;">{safe_value(m.get("price"), 0):,} PKR</b></p>
                                <p style="margin:2px 0;">Specs: <b>{safe_value(m.get("marla"))} Marla</b></p>
                                <p style="margin:2px 0; color:#475569; font-size:12px;">Utilities Available: {g_tag}{w_tag}{e_tag}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            msg = (
                                f"Salam {selected_client}, we found a matching property for you in "
                                f"{safe_value(m.get('area'))}. Size: {safe_value(m.get('marla'))} Marla. "
                                f"Rent/Price: {safe_value(m.get('price'), 0):,} PKR. Let me know if you want to visit."
                            )
                            phone = clean_phone(client.get("client_contact"))
                            if phone and m.get("id"):
                                st.link_button(f"Share Deal with {selected_client} via WhatsApp", f"https://wa.me/{phone}?text={quote(msg)}", key=f"wa_{m['id']}")
                    else:
                        st.warning("No properties matching this budget or type available.")
                except Exception as e:
                    st.error(f"Error in engine: {e}")
    else:
        st.info("No client records to test match.")

# -----------------------------
# 6. FINANCE
# -----------------------------
elif st.session_state.current_nav == "Finance":
    st.title("Financial Accounts Ledger")
    if st.session_state.role != "Admin":
        st.error("Access Denied.")
    else:
        with st.form("finance_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            entry_type = c1.selectbox("Transaction Type", ["Income", "Expense"])
            amount = c2.number_input("Amount (PKR)", min_value=0, step=1000)
            description = st.text_area("Description / Remarks")
            if st.form_submit_button("Commit Entry"):
                try:
                    supabase.table("accounts").insert({"type": entry_type, "amount": amount, "description": description}).execute()
                    st.success("Entry saved successfully.")
                except Exception as e:
                    st.error(f"Failed: {e}")

        st.markdown("---")
        try:
            finance_data = supabase.table("accounts").select("*").order("id", desc=True).execute().data
            if finance_data:
                df_fin = pd.DataFrame(finance_data)
                cols = [c for c in ["id", "type", "amount", "description"] if c in df_fin.columns]
                st.dataframe(df_fin[cols], use_container_width=True, hide_index=True)
        except Exception as e:
            pass

# -----------------------------
# 7. ACTIVITY LOGS
# -----------------------------
elif st.session_state.current_nav == "Activity Logs":
    st.title("System Audit Logs")
    if st.session_state.role != "Admin":
        st.error("Restricted area.")
    else:
        try:
            logs = supabase.table("activity_logs").select("*").order("created_at", desc=True).execute().data
            if logs:
                df_logs = pd.DataFrame(logs)
                cols = [c for c in ["created_at", "user", "action"] if c in df_logs.columns]
                st.dataframe(df_logs[cols], use_container_width=True, hide_index=True)
        except Exception as e:
            pass
