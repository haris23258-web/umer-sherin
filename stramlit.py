import streamlit as st
from supabase import create_client
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(page_title="Pindi-Isloo Real Estate ERP", layout="wide")

# --- DATABASE CONNECTION ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Secrets missing! Add SUPABASE_URL and SUPABASE_KEY in Streamlit settings.")
    st.stop()

# --- AUTHENTICATION ---
ADMIN_USERS = {
    "sawer khan": "sawer123",
    "tariq": "tariq456",
    "admin3": "pindi786"
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Twin Cities Estate Login")
    with st.form("login_form"):
        user = st.text_input("Username").lower().strip()
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user in ADMIN_USERS and ADMIN_USERS[user] == pwd:
                st.session_state["authenticated"] = True
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    st.stop()

# --- APP LOGIC ---
st.sidebar.title(f"🏢 Admin: {st.session_state['user'].title()}")
menu = ["📊 Dashboard", "🏠 Add Property", "👥 Clients & Matching", "📋 Inventory Manager"]
choice = st.sidebar.radio("Main Menu", menu)

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()

# --- 4. DASHBOARD ---
if choice == "📊 Dashboard":
    st.title("📈 Real Estate Analytics")
    
    # Data fetch for reporting
    inv_data = supabase.table("inventory").select("*").execute().data
    cli_data = supabase.table("clients").select("*").execute().data
    
    df_inv = pd.DataFrame(inv_data) if inv_data else pd.DataFrame()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Listings", len(inv_data) if inv_data else 0)
    col2.metric("Active Clients", len(cli_data) if cli_data else 0)
    
    if not df_inv.empty:
        col3.metric("Available Rent", len(df_inv[(df_inv['property_type'] == 'Rent') & (df_inv['status'] == 'Available')]))
        col4.metric("Available Sale", len(df_inv[(df_inv['property_type'] == 'Sale') & (df_inv['status'] == 'Available')]))

    st.divider()
    st.subheader("Quick View")
    if not df_inv.empty:
        st.write("Recent Activity in Pindi/Islamabad Markets:")
        st.dataframe(df_inv[['area', 'price', 'property_type', 'status']].tail(5), use_container_width=True)

# --- 5. ADD PROPERTY ---
elif choice == "🏠 Add Property":
    st.title("📝 Add New Listing")
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        p_type = c1.selectbox("Deal Type", ["Rent", "Sale"])
        area = c2.text_input("Specific Area (e.g., G-13/4, Bahria Phase 8)")
        
        c3, c4, c5 = st.columns(3)
        price = c3.number_input("Demand (PKR)", min_value=0, step=5000)
        beds = c4.number_input("Beds", min_value=0, max_value=20)
        marla = c5.number_input("Size (Marla/Kanal)", min_value=0.1)
        
        portion = st.selectbox("Portion/Type", ["Full House", "Upper Portion", "Lower Portion", "Flat", "Basement", "Room", "Office"])
        
        st.subheader("⚡ Utilities Information")
        u1, u2, u3 = st.columns(3)
        gas = u1.selectbox("Gas", ["No Gas", "Available (Separate)", "Available (Combined)"])
        water = u2.selectbox("Water", ["Boring Only", "Govt Supply", "Supply + Boring", "Tanker Only"])
        elec = u3.selectbox("Electricity", ["Separate Meter", "Combined Meter", "Solar System"])
        
        st.subheader("🔑 Confidential Owner Info")
        o_name = st.text_input("Owner Name")
        o_phone = st.text_input("Owner Contact (WhatsApp/Call)")
        
        if st.form_submit_button("Submit to Database"):
            new_data = {
                "added_by": st.session_state["user"],
                "property_type": p_type, "area": area, "price": price,
                "beds": beds, "marla": marla, "portion": portion,
                "gas": gas, "water": water, "electricity": elec,
                "owner_name": o_name, "owner_contact": o_phone, "status": "Available"
            }
            supabase.table("inventory").insert(new_data).execute()
            st.success(f"Property in {area} has been successfully added!")

# --- 6. CLIENTS & MATCHING ---
elif choice == "👥 Clients & Matching":
    st.title("🤝 Client Requirements & Smart Match")
    t1, t2 = st.tabs(["Register Client", "Run Matching Algorithm"])
    
    with t1:
        with st.form("cli_form"):
            name = st.text_input("Client Name")
            phone = st.text_input("Phone Number")
            req = st.selectbox("Looking for", ["Rent", "Sale"])
            budget = st.number_input("Max Budget", min_value=0)
            pref = st.text_input("Preferred Areas")
            if st.form_submit_button("Save Requirement"):
                supabase.table("clients").insert({
                    "client_name": name, "phone_number": phone, 
                    "requirement_type": req, "budget_max": budget, "area_preference": pref
                }).execute()
                st.success("Client requirement saved!")

    with t2:
        clients = supabase.table("clients").select("*").execute().data
        if clients:
            target = st.selectbox("Select Client to Match", [c['client_name'] for c in clients])
            c_info = next(i for i in clients if i['client_name'] == target)
            
            # Logic: Match Type and Price <= Budget
            matches = supabase.table("inventory").select("*")\
                .eq("property_type", c_info['requirement_type'])\
                .lte("price", c_info['budget_max'])\
                .eq("status", "Available")\
                .execute().data
            
            if matches:
                st.write(f"Found {len(matches)} options for {target}:")
                for m in matches:
                    with st.expander(f"📍 {m['area']} - {m['price']:,} PKR"):
                        st.write(f"**Contact:** {m['owner_contact']} ({m['owner_name']})")
                        st.write(f"**Utilities:** Gas: {m['gas']} | Water: {m['water']} | Elec: {m['electricity']}")
            else:
                st.warning("No matches found within budget.")

# --- 7. VIEW INVENTORY ---
elif choice == "📋 Inventory Manager":
    st.title("📂 Property Records")
    search = st.text_input("🔍 Search by Area, Owner or Portion")
    
    inv = supabase.table("inventory").select("*").order("created_at", desc=True).execute().data
    if inv:
        for p in inv:
            if search.lower() in p['area'].lower() or search.lower() in p['owner_name'].lower():
                with st.expander(f"🏠 {p['area']} | {p['property_type']} | {p['price']:,} PKR"):
                    col_info, col_action = st.columns([3, 1])
                    with col_info:
                        st.write(f"**Owner:** {p['owner_name']} - {p['owner_contact']}")
                        st.write(f"**Specs:** {p['beds']} Bed, {p['marla']} Marla, {p['portion']}")
                        st.write(f"**Utilities:** 🔥 {p['gas']} | 💧 {p['water']} | ⚡ {p['electricity']}")
                    with col_action:
                        new_status = st.selectbox("Status", ["Available", "Sold", "Rented"], key=f"st_{p['id']}", index=["Available", "Sold", "Rented"].index(p['status']))
                        if st.button("Update", key=f"up_{p['id']}"):
                            supabase.table("inventory").update({"status": new_status}).eq("id", p['id']).execute()
                            st.rerun()
                        if st.button("🗑️ Delete", key=f"dl_{p['id']}"):
                            supabase.table("inventory").delete().eq("id", p['id']).execute()
                            st.rerun()
