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
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}
.main-card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 18px;
}
.small-title {
    font-size: 18px;
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 10px;
}
.status-badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
}
.available {
    background: #dcfce7;
    color: #166534;
}
.hold {
    background: #fef3c7;
    color: #92400e;
}
.sold {
    background: #fee2e2;
    color: #991b1b;
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
    if status == "Available":
        return "available"
    elif status == "Sold":
        return "sold"
    return "hold"

# -----------------------------
# LOGIN USERS
# -----------------------------
USER_DB = {
    "sawer khan": {"role": "Admin", "pin": "sawer123"},
    "tariq": {"role": "Admin", "pin": "tariq456"},
    "agent": {"role": "Agent", "pin": "786"}
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("EstateFlow Pro Login")

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
    st.title("EstateFlow Pro")
    st.write(f"**User:** {st.session_state.user.title()}")
    st.caption(f"Role: {st.session_state.role}")
    st.divider()

    nav = st.radio("Select Module", [
        "Dashboard",
        "Quick Entry",
        "Properties",
        "Clients",
        "Deal Matcher",
        "Finance",
        "Activity Logs"
    ])

    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# -----------------------------
# DASHBOARD
# -----------------------------
if nav == "Dashboard":
    st.title("Dashboard")

    try:
        inventory = supabase.table("inventory").select("*").execute().data
        clients = supabase.table("clients").select("*").execute().data
        accounts = supabase.table("accounts").select("*").execute().data
    except Exception as e:
        st.error(f"Failed to load dashboard data: {e}")
        st.stop()

    total_inventory = len(inventory) if inventory else 0
    total_clients = len(clients) if clients else 0

    total_revenue = 0
    if accounts:
        df_acc = pd.DataFrame(accounts)
        if "type" in df_acc.columns and "amount" in df_acc.columns:
            total_revenue = df_acc[df_acc["type"] == "Income"]["amount"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Properties", total_inventory)
    col2.metric("Total Clients", total_clients)

    if st.session_state.role == "Admin":
        col3.metric("Revenue", f"{int(total_revenue):,} PKR")

    st.markdown("---")

    if inventory:
        df_inv = pd.DataFrame(inventory)

        c1, c2 = st.columns(2)

        with c1:
            if "area" in df_inv.columns:
                st.subheader("Properties by Area")
                st.bar_chart(df_inv["area"].value_counts())

        with c2:
            if "property_type" in df_inv.columns:
                st.subheader("Sale vs Rent")
                st.bar_chart(df_inv["property_type"].value_counts())
    else:
        st.info("No inventory data found.")

# -----------------------------
# QUICK ENTRY
# -----------------------------
elif nav == "Quick Entry":
    st.title("Quick Entry")

    tab1, tab2 = st.tabs(["House for Rent", "Client Entry"])

    # HOUSE FOR RENT
    with tab1:
        st.subheader("Add House for Rent")

        with st.form("quick_rent_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            area = c1.text_input("Area")
            marla = c2.number_input("Size (Marla)", min_value=1.0, step=1.0)
            rent_price = c3.number_input("Rent Price", min_value=0, step=1000)

            c4, c5, c6 = st.columns(3)
            category = c4.selectbox("Category", ["House", "Flat", "Portion", "Room"])
            status = c5.selectbox("Status", ["Available", "Hold"])
            owner_name = c6.text_input("Owner Name")

            owner_contact = st.text_input("Owner Contact")

            save_rent = st.form_submit_button("Save Property")

            if save_rent:
                if not area or not owner_name or not owner_contact:
                    st.warning("Please fill required fields.")
                else:
                    try:
                        supabase.table("inventory").insert({
                            "area": area,
                            "price": rent_price,
                            "marla": marla,
                            "property_type": "Rent",
                            "sub_type": category,
                            "status": status,
                            "owner_name": owner_name,
                            "owner_contact": owner_contact,
                            "added_by": st.session_state.user
                        }).execute()

                        supabase.table("activity_logs").insert({
                            "user": st.session_state.user,
                            "action": f"Added rent property in {area}"
                        }).execute()

                        st.success("Rent property added successfully.")
                    except Exception as e:
                        st.error(f"Failed to save property: {e}")

        st.markdown("---")
        st.subheader("Rent Property History")

        try:
            rent_history = supabase.table("inventory") \
                .select("*") \
                .eq("property_type", "Rent") \
                .order("id", desc=True) \
                .execute().data

            if rent_history:
                df_rent = pd.DataFrame(rent_history)
                cols = [c for c in [
                    "id", "area", "marla", "sub_type", "price",
                    "status", "owner_name", "owner_contact", "added_by"
                ] if c in df_rent.columns]
                st.dataframe(df_rent[cols], use_container_width=True)
            else:
                st.info("No rent history found.")
        except Exception as e:
            st.error(f"Failed to load rent history: {e}")

    # CLIENT ENTRY
    with tab2:
        st.subheader("Add Client")

        with st.form("quick_client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            client_name = c1.text_input("Client Name")
            client_contact = c2.text_input("Client Contact")

            c3, c4 = st.columns(2)
            demand_type = c3.selectbox("Demand Type", ["Sale", "Rent"])
            max_budget = c4.number_input("Max Budget", min_value=0, step=1000)

            save_client = st.form_submit_button("Save Client")

            if save_client:
                if not client_name or not client_contact:
                    st.warning("Please fill required fields.")
                else:
                    try:
                        supabase.table("clients").insert({
                            "client_name": client_name,
                            "client_contact": client_contact,
                            "demand_type": demand_type,
                            "max_budget": max_budget
                        }).execute()

                        supabase.table("activity_logs").insert({
                            "user": st.session_state.user,
                            "action": f"Added client {client_name}"
                        }).execute()

                        st.success("Client added successfully.")
                    except Exception as e:
                        st.error(f"Failed to save client: {e}")

        st.markdown("---")
        st.subheader("Client History")

        try:
            client_history = supabase.table("clients") \
                .select("*") \
                .order("id", desc=True) \
                .execute().data

            if client_history:
                df_clients = pd.DataFrame(client_history)
                cols = [c for c in [
                    "id", "client_name", "client_contact",
                    "demand_type", "max_budget"
                ] if c in df_clients.columns]
                st.dataframe(df_clients[cols], use_container_width=True)
            else:
                st.info("No client history found.")
        except Exception as e:
            st.error(f"Failed to load client history: {e}")

# -----------------------------
# PROPERTIES
# -----------------------------
elif nav == "Properties":
    st.title("All Properties")

    search = st.text_input("Search by Area")

    try:
        properties = supabase.table("inventory") \
            .select("*") \
            .ilike("area", f"%{search}%") \
            .order("id", desc=True) \
            .execute().data

        if properties:
            for p in properties:
                s = safe_value(p.get("status"))
                s_class = status_class(s)

                st.markdown(f"""
                <div class="main-card">
                    <span class="status-badge {s_class}">{s}</span>
                    <div class="small-title">📍 {safe_value(p.get("area"))}</div>
                    <p><b>{safe_value(p.get("marla"))} Marla {safe_value(p.get("sub_type"))}</b></p>
                    <p>Type: <b>{safe_value(p.get("property_type"))}</b></p>
                    <p>Price: <b>{safe_value(p.get("price"), 0):,} PKR</b></p>
                    <p>Owner: {safe_value(p.get("owner_name"))} | {safe_value(p.get("owner_contact"))}</p>
                </div>
                """, unsafe_allow_html=True)

                if (
                    st.session_state.role == "Admin"
                    and p.get("status") == "Available"
                    and p.get("id")
                ):
                    if st.button(f"Mark as Sold #{p['id']}"):
                        supabase.table("inventory").update({
                            "status": "Sold"
                        }).eq("id", p["id"]).execute()
                        st.rerun()
        else:
            st.info("No properties found.")
    except Exception as e:
        st.error(f"Failed to load properties: {e}")

# -----------------------------
# CLIENTS
# -----------------------------
elif nav == "Clients":
    st.title("All Clients")

    try:
        clients = supabase.table("clients") \
            .select("*") \
            .order("id", desc=True) \
            .execute().data

        if clients:
            df_clients = pd.DataFrame(clients)
            cols = [c for c in [
                "id", "client_name", "client_contact",
                "demand_type", "max_budget"
            ] if c in df_clients.columns]
            st.dataframe(df_clients[cols], use_container_width=True)
        else:
            st.info("No clients found.")
    except Exception as e:
        st.error(f"Failed to load clients: {e}")

# -----------------------------
# DEAL MATCHER
# -----------------------------
elif nav == "Deal Matcher":
    st.title("Deal Matcher")

    try:
        clients = supabase.table("clients").select("*").execute().data
    except Exception as e:
        st.error(f"Failed to load clients: {e}")
        st.stop()

    if clients:
        client_names = [c["client_name"] for c in clients if "client_name" in c]

        if client_names:
            selected_client = st.selectbox("Select Client", client_names)
            client = next((x for x in clients if x.get("client_name") == selected_client), None)

            if client:
                demand_type = client.get("demand_type")
                budget = client.get("max_budget", 0)

                try:
                    matched = supabase.table("inventory") \
                        .select("*") \
                        .eq("property_type", demand_type) \
                        .lte("price", budget * 1.1) \
                        .eq("status", "Available") \
                        .execute().data

                    if matched:
                        for m in matched:
                            score = 100
                            if m.get("price", 0) > budget:
                                score -= 15

                            st.markdown(f"""
                            <div class="main-card">
                                <div class="small-title">Match Score: {score}%</div>
                                <p>📍 <b>{safe_value(m.get("area"))}</b></p>
                                <p>Price: <b>{safe_value(m.get("price"), 0):,} PKR</b></p>
                                <p>Size: <b>{safe_value(m.get("marla"))} Marla</b></p>
                            </div>
                            """, unsafe_allow_html=True)

                            msg = (
                                f"Salam {selected_client}, we found a matching property for you in "
                                f"{safe_value(m.get('area'))}. Demand: {safe_value(m.get('price'), 0):,} PKR. "
                                f"Contact us for details."
                            )

                            phone = clean_phone(client.get("client_contact"))

                            if phone:
                                st.link_button(
                                    "Send to WhatsApp",
                                    f"[wa.me](https://wa.me/{phone}?text={quote(msg)})"
                                )
                    else:
                        st.warning("No matching property found.")
                except Exception as e:
                    st.error(f"Failed to match property: {e}")
    else:
        st.info("No clients available.")

# -----------------------------
# FINANCE
# -----------------------------
elif nav == "Finance":
    st.title("Finance")

    if st.session_state.role != "Admin":
        st.error("Only admin can access finance.")
    else:
        with st.form("finance_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            entry_type = c1.selectbox("Transaction Type", ["Income", "Expense"])
            amount = c2.number_input("Amount", min_value=0, step=1000)
            description = st.text_area("Description")

            save_finance = st.form_submit_button("Save Entry")

            if save_finance:
                try:
                    supabase.table("accounts").insert({
                        "type": entry_type,
                        "amount": amount,
                        "description": description
                    }).execute()

                    st.success("Finance entry saved.")
                except Exception as e:
                    st.error(f"Failed to save finance entry: {e}")

        st.markdown("---")

        try:
            finance_data = supabase.table("accounts") \
                .select("*") \
                .order("id", desc=True) \
                .execute().data

            if finance_data:
                df_fin = pd.DataFrame(finance_data)
                cols = [c for c in ["id", "type", "amount", "description"] if c in df_fin.columns]
                st.dataframe(df_fin[cols], use_container_width=True)
            else:
                st.info("No finance history found.")
        except Exception as e:
            st.error(f"Failed to load finance history: {e}")

# -----------------------------
# ACTIVITY LOGS
# -----------------------------
elif nav == "Activity Logs":
    st.title("Activity Logs")

    if st.session_state.role != "Admin":
        st.error("Only admin can view logs.")
    else:
        try:
            logs = supabase.table("activity_logs") \
                .select("*") \
                .order("created_at", desc=True) \
                .execute().data

            if logs:
                df_logs = pd.DataFrame(logs)
                cols = [c for c in ["created_at", "user", "action"] if c in df_logs.columns]
                st.dataframe(df_logs[cols], use_container_width=True)
            else:
                st.info("No activity logs found.")
        except Exception as e:
            st.error(f"Failed to load logs: {e}")
