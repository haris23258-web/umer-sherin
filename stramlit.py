import streamlit as st
from supabase import create_client
import pandas as pd
from urllib.parse import quote
import re

# -------------------------------
# 1. CONFIG & THEME
# -------------------------------
st.set_page_config(page_title="Estate Pro v8.0 | Enterprise ERP", layout="wide")

st.markdown("""
<style>
.stApp {
    background-color: #f8fafc;
}
.property-card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    border-top: 5px solid #1e40af;
    margin-bottom: 20px;
}
.metric-card {
    background: #ffffff;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    text-align: center;
}
.status-pill {
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
}
.available {
    background: #dcfce7;
    color: #166534;
}
.sold {
    background: #fee2e2;
    color: #991b1b;
}
.hold {
    background: #fef3c7;
    color: #92400e;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 2. DB CONNECTION
# -------------------------------
try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
except Exception as e:
    st.error(f"⚠️ Connection Failed: {e}")
    st.stop()

# -------------------------------
# 3. HELPERS
# -------------------------------
def clean_phone(phone):
    if phone is None:
        return ""
    return re.sub(r"[^0-9]", "", str(phone))

def safe_get(data, key, default=""):
    return data[key] if key in data and data[key] is not None else default

# -------------------------------
# 4. AUTH SYSTEM
# -------------------------------
USER_DB = {
    "sawer khan": {"role": "Admin", "pin": "sawer123"},
    "tariq": {"role": "Admin", "pin": "tariq456"},
    "agent": {"role": "Agent", "pin": "786"}
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🛡️ Enterprise Realty Gateway")
    with st.container(border=True):
        uid = st.text_input("User ID").lower().strip()
        upin = st.text_input("Access PIN", type="password")

        if st.button("Enter System", use_container_width=True):
            if uid in USER_DB and USER_DB[uid]["pin"] == upin:
                st.session_state.authenticated = True
                st.session_state.user = uid
                st.session_state.role = USER_DB[uid]["role"]
                st.rerun()
            else:
                st.error("Access Denied")
    st.stop()

# -------------------------------
# 5. SIDEBAR
# -------------------------------
with st.sidebar:
    st.title("🏗️ Estate Pro v8")
    st.write(f"Logged in: **{st.session_state.user.upper()}**")
    st.caption(f"Access Level: {st.session_state.role}")
    st.divider()

    nav = st.radio("ERP MODULES", [
        "🟢 Simple Entry",
        "📊 Analytics Dashboard",
        "🏠 Inventory Engine",
        "🎯 AI Deal Matcher",
        "💰 Finance & Payroll",
        "📑 Activity Logs"
    ])

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# -------------------------------
# 6. SIMPLE ENTRY
# -------------------------------
if nav == "🟢 Simple Entry":
    st.title("Simple Property & Client Entry")

    tab1, tab2 = st.tabs(["🏠 House for Rent", "👤 Client List"])

    # --- House for Rent ---
    with tab1:
        st.subheader("Add House for Rent")

        with st.form("simple_rent_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            area = c1.text_input("Area")
            price = c2.number_input("Rent Price (PKR)", min_value=0, step=1000)
            marla = c3.number_input("Size (Marla)", min_value=1.0, step=1.0)

            c4, c5, c6 = st.columns(3)
            sub_type = c4.selectbox("Category", ["House", "Flat", "Portion", "Room"])
            status = c5.selectbox("Status", ["Available", "Hold"])
            owner_name = c6.text_input("Owner Name")

            owner_contact = st.text_input("Owner Contact")

            submit_rent = st.form_submit_button("Save House for Rent")

            if submit_rent:
                if not area or not owner_name or not owner_contact:
                    st.warning("Please fill all required fields.")
                else:
                    try:
                        supabase.table("inventory").insert({
                            "area": area,
                            "price": price,
                            "marla": marla,
                            "property_type": "Rent",
                            "sub_type": sub_type,
                            "status": status,
                            "owner_name": owner_name,
                            "owner_contact": owner_contact,
                            "added_by": st.session_state.user
                        }).execute()

                        supabase.table("activity_logs").insert({
                            "user": st.session_state.user,
                            "action": f"Added Rent Property in {area}"
                        }).execute()

                        st.success("House for rent added successfully.")
                    except Exception as e:
                        st.error(f"Error saving property: {e}")

        st.markdown("---")
        st.subheader("House for Rent History")

        try:
            rent_history = supabase.table("inventory") \
                .select("*") \
                .eq("property_type", "Rent") \
                .order("id", desc=True) \
                .execute().data

            if rent_history:
                df_rent = pd.DataFrame(rent_history)
                show_cols = [col for col in [
                    "id", "area", "marla", "sub_type", "price",
                    "status", "owner_name", "owner_contact", "added_by"
                ] if col in df_rent.columns]
                st.dataframe(df_rent[show_cols], use_container_width=True)
            else:
                st.info("No rent property history found.")
        except Exception as e:
            st.error(f"Error loading rent history: {e}")

    # --- Client List ---
    with tab2:
        st.subheader("Add Client Entry")

        with st.form("simple_client_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            client_name = c1.text_input("Client Name")
            client_contact = c2.text_input("Client Contact")

            c3, c4 = st.columns(2)
            demand_type = c3.selectbox("Demand Type", ["Sale", "Rent"])
            max_budget = c4.number_input("Max Budget (PKR)", min_value=0, step=1000)

            submit_client = st.form_submit_button("Save Client")

            if submit_client:
                if not client_name or not client_contact:
                    st.warning("Please fill all required fields.")
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
                            "action": f"Added Client {client_name}"
                        }).execute()

                        st.success("Client added successfully.")
                    except Exception as e:
                        st.error(f"Error saving client: {e}")

        st.markdown("---")
        st.subheader("Client History")

        try:
            client_history = supabase.table("clients") \
                .select("*") \
                .order("id", desc=True) \
                .execute().data

            if client_history:
                df_clients = pd.DataFrame(client_history)
                show_cols = [col for col in [
                    "id", "client_name", "client_contact",
                    "demand_type", "max_budget"
                ] if col in df_clients.columns]
                st.dataframe(df_clients[show_cols], use_container_width=True)
            else:
                st.info("No client history found.")
        except Exception as e:
            st.error(f"Error loading client history: {e}")

# -------------------------------
# 7. ANALYTICS DASHBOARD
# -------------------------------
elif nav == "📊 Analytics Dashboard":
    st.title("Market Intelligence Dashboard")

    try:
        inv = supabase.table("inventory").select("*").execute().data
        cli = supabase.table("clients").select("*").execute().data
        acc = supabase.table("accounts").select("*").execute().data
    except Exception as e:
        st.error(f"Data fetch error: {e}")
        st.stop()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.metric("Live Inventory", len(inv) if inv else 0)

    with kpi2:
        st.metric("Hot Leads", len(cli) if cli else 0)

    if st.session_state.role == "Admin" and acc:
        df_acc = pd.DataFrame(acc)
        if "type" in df_acc.columns and "amount" in df_acc.columns:
            rev = df_acc[df_acc["type"] == "Income"]["amount"].sum()
            with kpi3:
                st.metric("Total Revenue", f"{rev:,} PKR")

    st.divider()

    c_left, c_right = st.columns(2)

    if inv:
        df_i = pd.DataFrame(inv)

        with c_left:
            if "area" in df_i.columns:
                st.subheader("📍 Inventory by Location")
                st.bar_chart(df_i["area"].value_counts())

        with c_right:
            if "property_type" in df_i.columns:
                st.subheader("🏠 Type Distribution")
                st.bar_chart(df_i["property_type"].value_counts())

# -------------------------------
# 8. INVENTORY ENGINE
# -------------------------------
elif nav == "🏠 Inventory Engine":
    st.title("Property Bank")
    t1, t2 = st.tabs(["➕ Add New Asset", "🔍 Browse Assets"])

    with t1:
        with st.form("add_prop", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            area = col1.text_input("Area (e.g. DHA Phase 2)")
            price = col2.number_input("Demand (PKR)", min_value=0)
            m_size = col3.number_input("Size (Marla)", min_value=1.0, step=1.0)

            col4, col5, col6 = st.columns(3)
            p_type = col4.selectbox("Type", ["Sale", "Rent"])
            p_cat = col5.selectbox("Category", ["House", "Plot", "Flat", "Commercial"])
            status = col6.selectbox("Status", ["Available", "Hold"])

            o_name = st.text_input("Owner Name")
            o_phone = st.text_input("Owner Contact")

            if st.form_submit_button("PUBLISH TO ERP"):
                try:
                    supabase.table("inventory").insert({
                        "area": area,
                        "price": price,
                        "marla": m_size,
                        "property_type": p_type,
                        "sub_type": p_cat,
                        "status": status,
                        "owner_name": o_name,
                        "owner_contact": o_phone,
                        "added_by": st.session_state.user
                    }).execute()

                    supabase.table("activity_logs").insert({
                        "user": st.session_state.user,
                        "action": f"Added {m_size} Marla in {area}"
                    }).execute()

                    st.success("Property Synced Globally!")
                except Exception as e:
                    st.error(f"Error adding property: {e}")

    with t2:
        search = st.text_input("Search Location...")

        try:
            data = supabase.table("inventory") \
                .select("*") \
                .ilike("area", f"%{search}%") \
                .execute().data

            if data:
                for p in data:
                    status_value = safe_get(p, "status", "")
                    if status_value == "Available":
                        status_class = "available"
                    elif status_value == "Sold":
                        status_class = "sold"
                    else:
                        status_class = "hold"

                    st.markdown(f"""
                    <div class="property-card">
                        <span class="status-pill {status_class}">{status_value}</span>
                        <h3>📍 {safe_get(p, "area", "")}</h3>
                        <p><b>{safe_get(p, "marla", "")} Marla {safe_get(p, "sub_type", "")}</b> for <b>{safe_get(p, "property_type", "")}</b></p>
                        <h4 style="color:#1e40af;">{safe_get(p, "price", 0):,} PKR</h4>
                        <hr>
                        <p>👤 {safe_get(p, "owner_name", "")} | 📞 {safe_get(p, "owner_contact", "")}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if (
                        st.session_state.role == "Admin"
                        and status_value == "Available"
                        and "id" in p
                    ):
                        if st.button(f"Mark as Sold", key=f"sold_{p['id']}"):
                            supabase.table("inventory").update({
                                "status": "Sold"
                            }).eq("id", p["id"]).execute()
                            st.rerun()
            else:
                st.info("No property found.")
        except Exception as e:
            st.error(f"Error loading inventory: {e}")

# -------------------------------
# 9. AI DEAL MATCHER
# -------------------------------
elif nav == "🎯 AI Deal Matcher":
    st.title("Smart Match & Auto-Alert")

    try:
        clients = supabase.table("clients").select("*").execute().data
    except Exception as e:
        st.error(f"Error loading clients: {e}")
        st.stop()

    if clients:
        client_names = [x["client_name"] for x in clients if "client_name" in x]

        if client_names:
            sel_c = st.selectbox("Select Target Client", client_names)
            c = next((x for x in clients if x.get("client_name") == sel_c), None)

            if c:
                demand_type = c.get("demand_type")
                max_budget = c.get("max_budget", 0)

                try:
                    matches = supabase.table("inventory") \
                        .select("*") \
                        .eq("property_type", demand_type) \
                        .lte("price", max_budget * 1.1) \
                        .eq("status", "Available") \
                        .execute().data
                except Exception as e:
                    st.error(f"Error matching properties: {e}")
                    st.stop()

                if matches:
                    for m in matches:
                        score = 100
                        if m.get("price", 0) > max_budget:
                            score -= 15

                        with st.container(border=True):
                            st.write(f"### Match Score: {score}%")
                            st.progress(score / 100)
                            st.write(f"🏠 **{safe_get(m, 'area', '')}** | Price: {safe_get(m, 'price', 0):,} PKR")

                            wa_text = (
                                f"Salam {sel_c}, we found a matching property for you in "
                                f"{safe_get(m, 'area', '')}. Demand: {safe_get(m, 'price', 0):,} PKR. "
                                f"Contact us for details."
                            )

                            phone = clean_phone(c.get("client_contact", ""))

                            if phone:
                                st.link_button(
                                    "📲 Push to WhatsApp",
                                    f"[wa.me](https://wa.me/{phone}?text={quote(wa_text)})"
                                )
                            else:
                                st.warning("Client contact number is missing or invalid.")
                else:
                    st.warning("No properties matching this client's profile.")
        else:
            st.info("No valid client names found.")
    else:
        st.info("No clients found.")

# -------------------------------
# 10. FINANCE & PAYROLL
# -------------------------------
elif nav == "💰 Finance & Payroll":
    st.title("Financial Ledger")

    if st.session_state.role != "Admin":
        st.error("Admin Access Required")
    else:
        with st.form("ledger_entry"):
            f1, f2 = st.columns(2)
            t_type = f1.selectbox("Transaction", ["Income", "Expense"])
            amt = f2.number_input("Amount (PKR)", min_value=0)
            desc = st.text_area("Details (Include Deal IDs)")

            if st.form_submit_button("Record Transaction"):
                try:
                    supabase.table("accounts").insert({
                        "type": t_type,
                        "amount": amt,
                        "description": desc
                    }).execute()
                    st.success("Ledger Updated!")
                except Exception as e:
                    st.error(f"Error saving transaction: {e}")

# -------------------------------
# 11. ACTIVITY LOGS
# -------------------------------
elif nav == "📑 Activity Logs":
    st.title("System Audit Trail")

    if st.session_state.role != "Admin":
        st.error("Access Denied")
    else:
        try:
            logs = supabase.table("activity_logs") \
                .select("*") \
                .order("created_at", desc=True) \
                .execute().data

            if logs:
                df_logs = pd.DataFrame(logs)
                show_cols = [col for col in ["created_at", "user", "action"] if col in df_logs.columns]
                st.table(df_logs[show_cols])
            else:
                st.info("No activity logs found.")
        except Exception as e:
            st.error(f"Error loading logs: {e}")

