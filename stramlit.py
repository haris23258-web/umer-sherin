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
# CUSTOM CSS FOR REFINED FINISHING
# -----------------------------
# CUSTOM CSS FOR REFINED FINISHING (MOBILE RESPONSIVE FIX)
# -----------------------------
st.markdown("""
<style>
/* Background & Core App Layout */
.stApp { background-color: #f8fafc; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* Elegant Minimalist Dashboard Cards */
.metric-container {
    display: flex;
    flex-wrap: wrap;
    gap: 1.2rem;
    margin-bottom: 2rem;
}
.kpi-card {
    flex: 1;
    min-width: 220px;
    background: #ffffff; 
    padding: 20px; 
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
    border: 1px solid #e2e8f0;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
.kpi-label {
    margin: 0;
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.kpi-value {
    margin: 6px 0 0 0;
    color: #0f172a;
    font-size: 24px;
    font-weight: 800;
}

/* Info and Content Boxes */
.report-box {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border-left: 4px solid #b45309;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.about-box {
    background-color: #f1f5f9;
    padding: 16px;
    border-radius: 12px;
    font-size: 13px;
    color: #334155;
    border: 1px solid #e2e8f0;
    margin-top: 20px;
    line-height: 1.5;
}

/* 📱 MOBILE RESPONSIVE & SIDEBAR STICKY TUNING */
@media (max-width: 768px) {
    /* Yeh force karega ki mobile par click ke baad bhi sidebar gayab na ho */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
    }
    section[data-testid="stSidebar"] {
        left: 0 !important;
        position: fixed !important;
        z-index: 999999 !important;
    }
    
    .metric-container {
        flex-direction: column;
        gap: 0.8rem;
    }
    .kpi-card {
        padding: 16px;
        min-width: 100%;
    }
    .kpi-value {
        font-size: 20px;
    }
    .block-container {
        padding-top: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
}
</style>
""", unsafe_allow_html=True)
# -----------------------------# -----------------------------
# CUSTOM CSS FOR REFINED FINISHING (MOBILE RESPONSIVE FIX)
# -----------------------------
st.markdown("""
<style>
/* Background & Core App Layout */
.stApp { background-color: #f8fafc; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* Elegant Minimalist Dashboard Cards */
.metric-container {
    display: flex;
    flex-wrap: wrap;
    gap: 1.2rem;
    margin-bottom: 2rem;
}
.kpi-card {
    flex: 1;
    min-width: 220px;
    background: #ffffff; 
    padding: 20px; 
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
    border: 1px solid #e2e8f0;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
.kpi-label {
    margin: 0;
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.kpi-value {
    margin: 6px 0 0 0;
    color: #0f172a;
    font-size: 24px;
    font-weight: 800;
}

/* Info and Content Boxes */
.report-box {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border-left: 4px solid #b45309;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.about-box {
    background-color: #f1f5f9;
    padding: 16px;
    border-radius: 12px;
    font-size: 13px;
    color: #334155;
    border: 1px solid #e2e8f0;
    margin-top: 20px;
    line-height: 1.5;
}

/* 📱 MOBILE RESPONSIVE & SIDEBAR STICKY TUNING */
@media (max-width: 768px) {
    /* Yeh force karega ki mobile par click ke baad bhi sidebar gayab na ho */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
    }
    section[data-testid="stSidebar"] {
        left: 0 !important;
        position: fixed !important;
        z-index: 999999 !important;
    }
    
    .metric-container {
        flex-direction: column;
        gap: 0.8rem;
    }
    .kpi-card {
        padding: 16px;
        min-width: 100%;
    }
    .kpi-value {
        font-size: 20px;
    }
    .block-container {
        padding-top: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
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
# CUSTOM CSS FOR REFINED FINISHING (MOBILE RESPONSIVE FIX)
# -----------------------------
st.markdown("""
<style>
/* Background & Core App Layout */
.stApp { background-color: #f8fafc; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* Elegant Minimalist Dashboard Cards */
.metric-container {
    display: flex;
    flex-wrap: wrap; /* Allows cards to wrap on smaller screens */
    gap: 1.2rem;
    margin-bottom: 2rem;
}
.kpi-card {
    flex: 1;
    min-width: 220px; /* Prevents cards from crushing into squished vertical bars */
    background: #ffffff; 
    padding: 20px; 
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
    border: 1px solid #e2e8f0;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
.kpi-label {
    margin: 0;
    color: #64748b;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.kpi-value {
    margin: 6px 0 0 0;
    color: #0f172a;
    font-size: 24px;
    font-weight: 800;
}

/* Info and Content Boxes */
.report-box {
    background-color: #ffffff;
    padding: 18px;
    border-radius: 12px;
    border-left: 4px solid #b45309;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.about-box {
    background-color: #f1f5f9;
    padding: 16px;
    border-radius: 12px;
    font-size: 13px;
    color: #334155;
    border: 1px solid #e2e8f0;
    margin-top: 20px;
    line-height: 1.5;
}

/* 📱 MOBILE RESPONSIVE TUNING */
@media (max-width: 768px) {
    .metric-container {
        flex-direction: column; /* Stacks cards vertically on mobile */
        gap: 0.8rem;
    }
    .kpi-card {
        padding: 16px; /* Reduced padding for mobile to save space */
        min-width: 100%;
    }
    .kpi-value {
        font-size: 20px; /* Slightly smaller text for compact layout */
    }
    .block-container {
        padding-top: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }
}
</style>
""", unsafe_allow_html=True)
# -----------------------------
# HELPERS & PDF GENERATOR
# -----------------------------
def clean_phone(phone):
    return re.sub(r"[^0-9]", "", str(phone)) if phone else ""

def log_activity(user, action, area="N/A"):
    try:
        supabase.table("activity_logs").insert({
            "user": user, 
            "action": action,
            "target_area": area,
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }).execute()
    except:
        pass

def convert_df_to_pdf_html(df, title):
    html = f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; }}
            h2 {{ color: #1e3a8a; border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; font-size: 12px; }}
            th {{ background-color: #f1f5f9; color: #1e3a8a; }}
            .footer {{ margin-top: 40px; font-size: 11px; color: #64748b; text-align: center; }}
        </style>
    </head>
    <body>
        <h2>🏢 DEEWARYN.COM - {title}</h2>
        <p><b>Generated On:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        {df.to_html(index=False)}
        <div class="footer">Bostan Khan Road, Chaklala Scheme 3, Rawalpindi | Phone: 0333-2002666</div>
    </body>
    </html>
    """
    return html

# -----------------------------
# LOGIN SYSTEM
# -----------------------------
USER_DB = {
    "sami": {"role": "Viewer", "pin": "sami786"},       # CEO / Viewer Role
    "umer": {"role": "Viewer", "pin": "umer123"},       # Owner / Viewer Role
    "sawer khan": {"role": "Agent", "pin": "sawer123"}, # Agent Role
    "tariq": {"role": "Agent", "pin": "tariq456"}       # Agent Role
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

if "local_deals" not in st.session_state:
    st.session_state.local_deals = []

# Pre-fetch baseline data safely
all_deals_list = []
try:
    db_deals = supabase.table("deals").select("*").execute().data
    if db_deals: all_deals_list.extend(db_deals)
except: pass
all_deals_list.extend(st.session_state.local_deals)

# -----------------------------
# SIDEBAR NAVIGATION & BRANDING
# -----------------------------
if "current_nav" not in st.session_state:
    st.session_state.current_nav = "Dashboard"

with st.sidebar:
    # Integrated user's beautiful golden logo file
    try:
        st.image("mehfooz deewaryn logo WITH SLOGEN.png", use_container_width=True)
    except:
        st.markdown("<h2 style='color:#b45309; margin-bottom:0;'>🏗️ DEEWARYN.COM</h2>", unsafe_allow_html=True)
    
    st.markdown(f"<div style='text-align: center; margin-bottom: 15px;'>👤 <b>{st.session_state.user.title()}</b> ({st.session_state.role})</div>", unsafe_allow_html=True)
    st.divider()
    
    modules = [{"name": "Dashboard", "icon": "📊"}]
    
    if st.session_state.role != "Viewer":
        modules.append({"name": "Quick Entry", "icon": "➕"})
        
    modules.extend([
        {"name": "Properties", "icon": "🏡"},
        {"name": "Clients", "icon": "👤"},
        {"name": "Property Visits Log", "icon": "📋"}
    ])
    
    if st.session_state.role != "Viewer":
        modules.append({"name": "Deal Done Registry", "icon": "🤝"})
        
    modules.extend([
        {"name": "Deals History", "icon": "📜"},          
        {"name": "Working Progress", "icon": "📈"},       
        {"name": "Deal Matcher", "icon": "🔍"},
        {"name": "Finance", "icon": "💰"},
        {"name": "Activity Logs", "icon": "📋"}
    ])
    
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
# 1. DASHBOARD MODULE (REFINISHED UI)
# -----------------------------
if st.session_state.current_nav == "Dashboard":
    st.title("📊 DEEWARYN.COM - Main Dashboard")
    
    inventory, clients_data, total_visits = [], [], 0
    try:
        inventory = supabase.table("inventory").select("*").execute().data
        clients_data = supabase.table("clients").select("*").execute().data
        visits_data = supabase.table("property_visits").select("id").execute().data
        total_visits = len(visits_data) if visits_data else 0
    except: pass

    # Elegant grid-based KPI visual display
    st.markdown(f"""
    <div class="metric-container">
        <div class="kpi-card" style="border-top: 4px solid #0f172a;">
            <p class="kpi-label">Total Properties</p>
            <p class="kpi-value">{len(inventory) if inventory else 0} Units</p>
        </div>
        <div class="kpi-card" style="border-top: 4px solid #0284c7;">
            <p class="kpi-label">Registered Clients</p>
            <p class="kpi-value">{len(clients_data) if clients_data else 0} Active</p>
        </div>
        <div class="kpi-card" style="border-top: 4px solid #d97706;">
            <p class="kpi-label">Total Visits Done</p>
            <p class="kpi-value">{total_visits} Visits</p>
        </div>
        <div class="kpi-card" style="border-top: 4px solid #16a34a;">
            <p class="kpi-label">Deals Closed</p>
            <p class="kpi-value">{len(all_deals_list)} Units</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.role == "Viewer":
        st.info(f"👋 Welcome! Aap is waqt **Watch-Only Admin Mode** mein hain. Aap poore staff ki working, gharon aur property visits ka live record dekh sakte hain.")

# -----------------------------
# 2. QUICK ENTRY MODULE
# -----------------------------
elif st.session_state.current_nav == "Quick Entry":
    if st.session_state.role == "Viewer":
        st.error("Aap ko is page tak rasai nahi hai.")
    else:
        st.title("Quick Entry Wizard")
        tab1, tab2, tab3, tab4 = st.tabs(["🏡 House for Rent Entry", "👤 Client Requirements Entry", "🚗 Staff Property Visits Entry", "🗣️ Staff Field Notes"])

        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_logged_agent = st.session_state.user

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
                                "visiting_time": f"{visiting_time} {utility_notes}".strip(), 
                                "added_by": current_logged_agent,
                                "created_at": current_timestamp
                            }).execute()
                            st.success(f"Rent property saved safely by {current_logged_agent.title()}!")
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
                                "client_name": client_name, "client_contact": client_contact,
                                "demand_type": demand_type, "max_budget": max_budget,
                                "preferred_area": combined_pref_details, "status": "Searching",
                                "added_by": current_logged_agent,
                                "created_at": current_timestamp
                            }).execute()
                            st.success(f"Client registered successfully!")
                        except Exception as e: st.error(f"Error: {e}")

        with tab3:
            st.subheader("🚗 Log a Property Visit with Client")
            with st.form("visit_entry_form", clear_on_submit=True):
                v_c1, v_c2 = st.columns(2)
                v_client = v_c1.text_input("Client Name (Whom you showed the house)")
                v_contact = v_c2.text_input("Client Contact Number / Mobile")
                v_property = st.text_input("Property / House Visited (Area & Details)")
                v_feedback = st.text_area("Client Feedback (e.g., Token promised, Disliked due to gas issue, Token given, etc.)")
                
                if st.form_submit_button("💾 Save Visit Entry"):
                    if not v_client or not v_property: st.warning("Please fill Client and Property details.")
                    else:
                        try:
                            final_feedback_str = f"[Contact: {v_contact}] {v_feedback}".strip() if v_contact else v_feedback
                            supabase.table("property_visits").insert({
                                "client_name": v_client,
                                "property_details": v_property,
                                "feedback": final_feedback_str,
                                "agent_name": current_logged_agent,
                                "created_at": current_timestamp
                            }).execute()
                            log_activity(current_logged_agent, f"Logged a property visit for client {v_client}", v_property)
                            st.success("🎉 Property visit entry recorded successfully!")
                        except Exception as e: st.error(f"Database error or Table missing: {e}")

        with tab4:
            st.subheader("📝 Record Staff Daily Field Notes")
            with st.form("staff_work_form", clear_on_submit=True):
                cw1, cw2 = st.columns(2)
                working_staff = cw1.text_input("Staff Member", value=st.session_state.user, disabled=True)
                working_area = cw2.text_input("Target Area Name")
                activity_detail = st.text_area("What general work was done today?")
                if st.form_submit_button("📢 Submit Notes"):
                    log_activity(working_staff, activity_detail, working_area)
                    st.success("Notes logged!")

# -----------------------------
# 3. PROPERTIES DATABASE
# -----------------------------
elif st.session_state.current_nav == "Properties":
    st.title("🏡 Properties Master Database")
    search = st.text_input("🔍 Search Property by Area Name")
    
    try:
        properties = supabase.table("inventory").select("*").ilike("area", f"%{search}%").order("id", desc=True).execute().data
        if properties:
            df_inv = pd.DataFrame(properties)
            all_cols = ["id", "created_at", "added_by", "area", "marla", "property_type", "sub_type", "price", "status", "owner_name", "owner_contact", "visiting_time"]
            display_cols = [c for c in all_cols if c in df_inv.columns]
            
            pdf_html = convert_df_to_pdf_html(df_inv[display_cols], "Properties Inventory Report")
            st.download_button(label="📥 Print PDF (Download Properties Report)", data=pdf_html, file_name="properties_report.html", mime="text/html")
            
            def style_prop_row(row):
                return ['background-color: #dcfce7; color: #166534; font-weight: bold;'] * len(row) if row.status in ["Rent Out", "Sold"] else [''] * len(row)
            
            st.dataframe(df_inv[display_cols].style.apply(style_prop_row, axis=1), use_container_width=True, hide_index=True)
            
            if st.session_state.role != "Viewer":
                st.markdown("### 🛠️ Property Action Controls")
                with st.container(border=True):
                    ac1, ac2, ac3 = st.columns([4, 2, 2])
                    prop_options = {f"ID: {p['id']} - {p['marla']} Marla ({p['area']}) [Current: {p['status']}]": p['id'] for p in properties}
                    selected_p_label = ac1.selectbox("Select Property Unit to update:", list(prop_options.keys()))
                    selected_p_id = prop_options[selected_p_label]
                    current_unit = next((item for item in properties if item["id"] == selected_p_id), None)
                    
                    if ac2.button("✅ Mark Selected Rent Out", use_container_width=True):
                        supabase.table("inventory").update({"status": "Rent Out"}).eq("id", selected_p_id).execute()
                        log_activity(st.session_state.user, f"Marked Property ID {selected_p_id} as Rent Out", current_unit['area'] if current_unit else "N/A")
                        st.success("Property marked as Rent Out!")
                        st.rerun()
                        
                    if ac3.button("🚨 Delete Property", use_container_width=True):
                        supabase.table("inventory").delete().eq("id", selected_p_id).execute()
                        st.warning("Property removed.")
                        st.rerun()
        else: st.info("No matching properties found.")
    except Exception as e: st.error(f"Error: {e}")

# -----------------------------
# 4. CLIENTS DATABASE
# -----------------------------
elif st.session_state.current_nav == "Clients":
    st.title("👥 Registered Clients Database")
    search_client = st.text_input("🔍 Search Client by Name")
    
    try:
        clients = supabase.table("clients").select("*").ilike("client_name", f"%{search_client}%").order("id", desc=True).execute().data
        if clients:
            df_clients = pd.DataFrame(clients)
            all_client_cols = ["id", "created_at", "added_by", "client_name", "client_contact", "demand_type", "max_budget", "preferred_area", "status"]
            display_cols = [c for c in all_client_cols if c in df_clients.columns]
            
            pdf_html = convert_df_to_pdf_html(df_clients[display_cols], "Registered Clients Requirements")
            st.download_button(label="📥 Print PDF (Download Clients Report)", data=pdf_html, file_name="clients_report.html", mime="text/html")
            
            def style_client_row(row):
                return ['background-color: #dcfce7; color: #166534; font-weight: bold;'] * len(row) if row.status == "House Found" else [''] * len(row)
            
            st.dataframe(df_clients[display_cols].style.apply(style_client_row, axis=1), use_container_width=True, hide_index=True)
            
            if st.session_state.role != "Viewer":
                st.markdown("### 🛠️ Client Status Update Control Center")
                with st.container(border=True):
                    cc_col1, cc_col2, cc_col3 = st.columns([4, 3, 3])
                    client_options = {f"ID: {c['id']} - {c['client_name']} [Status: {c['status']}]": c['id'] for c in clients}
                    sel_client_label = cc_col1.selectbox("Select Target Client:", list(client_options.keys()))
                    sel_client_id = client_options[sel_client_label]
                    current_client_record = next((x for x in clients if x["id"] == sel_client_id), None)
                    
                    if cc_col2.button("🤝 Mark Status: House Found", use_container_width=True):
                        supabase.table("clients").update({"status": "House Found"}).eq("id", sel_client_id).execute()
                        log_activity(st.session_state.user, f"Marked Client {current_client_record['client_name']} as House Found", current_client_record.get('preferred_area', 'N/A') if current_client_record else "N/A")
                        st.success("Client marked as House Found successfully!")
                        st.rerun()
                    
                    if cc_col3.button("🚨 Delete Client From System", use_container_width=True):
                        supabase.table("clients").delete().eq("id", sel_client_id).execute()
                        st.warning("Client profile removed.")
                        st.rerun()
        else: st.info("No registered clients match this name.")
    except Exception as e: st.error(f"Error handling system display: {e}")

# -----------------------------
# 5. PROPERTY VISITS LOG (WITH REFINED DELETE)
# -----------------------------
elif st.session_state.current_nav == "Property Visits Log":
    st.title("📋 Staff Daily Property Visits Record Room")
    
    try:
        visits = supabase.table("property_visits").select("*").order("id", desc=True).execute().data
        if visits:
            df_visits = pd.DataFrame(visits)[["id", "created_at", "agent_name", "client_name", "property_details", "feedback"]]
            df_visits_display = df_visits[["created_at", "agent_name", "client_name", "property_details", "feedback"]]
            df_visits_display.columns = ["Date & Time", "Agent Name", "Client Name", "Property Visited", "Client Feedback / Remarks"]
            
            pdf_html = convert_df_to_pdf_html(df_visits_display, "Daily Property Visits Report")
            st.download_button(label="📥 Print PDF (Download Visits Report Log)", data=pdf_html, file_name="property_visits_report.html", mime="text/html")
            
            st.dataframe(df_visits_display, use_container_width=True, hide_index=True)
            
            # Delete Control Widget
            if st.session_state.role != "Viewer":
                st.markdown("### 🛠️ Remove/Delete Visit Entry")
                with st.container(border=True):
                    del_v1, del_v2 = st.columns([5, 3])
                    visit_options = {f"ID: {v['id']} - Client: {v['client_name']} (Agent: {v['agent_name']})": v['id'] for v in visits}
                    selected_visit_label = del_v1.selectbox("Select Visit Entry to Delete:", list(visit_options.keys()))
                    selected_visit_id = visit_options[selected_visit_label]
                    
                    if del_v2.button("🚨 Delete Selected Visit Log", use_container_width=True):
                        supabase.table("property_visits").delete().eq("id", selected_visit_id).execute()
                        log_activity(st.session_state.user, f"Deleted Visit Log Entry ID: {selected_visit_id}")
                        st.warning("Visit record row removed successfully.")
                        st.rerun()
        else:
            st.info("Abhi tak system mein koi Property Visit report enter nahi ki gayi.")
    except Exception as e:
        st.error(f"Error loading visits log: {e}")

# -----------------------------
# 6. DEAL DONE REGISTRY
# -----------------------------
elif st.session_state.current_nav == "Deal Done Registry":
    if st.session_state.role == "Viewer":
        st.error("Aap ko is page tak rasai nahi hai.")
    else:
        st.title("🤝 Deal Closure & Done Registry")
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
            else: selected_house = f_c1.text_input("Manual Property Entry")
                
            if db_clients:
                client_list = [f"ID: {c['id']} - {c['client_name']} ({c['preferred_area']})" for c in db_clients]
                selected_client = f_c2.selectbox("Select Registered Client:", client_list)
            else: selected_client = f_c2.text_input("Manual Client Entry")
                
            f_c3, f_c4 = st.columns(2)
            closing_agent = f_c3.selectbox("Which Staff Member closed this deal?", ["sawer khan", "tariq"])
            deal_commission = f_c4.number_input("Commission Earned (PKR)", min_value=0, value=20000, step=5000)
            deal_area = st.text_input("Deal Location / Area Name")

            if st.form_submit_button("🚀 Finalize and Lock This Deal"):
                if not selected_house or not selected_client: st.error("Details missing!")
                else:
                    try:
                        final_house_str, final_client_str = str(selected_house), str(selected_client)
                        try:
                            if "ID:" in final_house_str:
                                p_id = int(final_house_str.split("-")[0].replace("ID:", "").strip())
                                supabase.table("inventory").update({"status": "Rent Out"}).eq("id", p_id).execute()
                        except: pass
                        try:
                            if "ID:" in final_client_str:
                                c_id = int(final_client_str.split("-")[0].replace("ID:", "").strip())
                                supabase.table("clients").update({"status": "House Found"}).eq("id", c_id).execute()
                        except: pass

                        new_deal_object = {
                            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "client_name": final_client_str.split("-")[-1].strip() if "-" in final_client_str else final_client_str,
                            "property_details": final_house_str, 
                            "agent_name": closing_agent, 
                            "commission_earned": deal_commission
                        }
                        supabase.table("deals").insert(new_deal_object).execute()
                        st.success("🔥 Deal Logged and Locked inside System Successfully!")
                        st.rerun()
                    except Exception as e: st.error(f"System Error: {e}")

# -----------------------------
# 7. DEALS HISTORY MODULE (WITH REFINED DELETE)
# -----------------------------
elif st.session_state.current_nav == "Deals History":
    st.title("📜 Successful Closed Deals History Log")
    if all_deals_list:
        df_deals_display = pd.DataFrame(all_deals_list)
        
        target_cols = ["id", "created_at", "client_name", "property_details", "agent_name", "commission_earned"]
        active_cols = [col for col in target_cols if col in df_deals_display.columns]
        
        pdf_html = convert_df_to_pdf_html(df_deals_display[active_cols], "Closed Deals Registry Report")
        st.download_button(label="📥 Print PDF (Download Deals Invoice History)", data=pdf_html, file_name="deals_history.html", mime="text/html")
        
        st.dataframe(df_deals_display[active_cols], use_container_width=True, hide_index=True)
        
        # Delete Deal Control Widget
        if st.session_state.role != "Viewer":
            st.markdown("### 🛠️ Remove/Delete Closed Deal Record")
            with st.container(border=True):
                del_d1, del_d2 = st.columns([5, 3])
                deal_options = {f"ID: {d['id']} - Client: {d['client_name']} (Earned: {d.get('commission_earned', 0)})": d['id'] for d in all_deals_list if 'id' in d}
                if deal_options:
                    selected_deal_label = del_d1.selectbox("Select Closed Deal Row to Remove:", list(deal_options.keys()))
                    selected_deal_id = deal_options[selected_deal_label]
                    
                    if del_d2.button("🚨 Delete Selected Deal Form Database", use_container_width=True):
                        supabase.table("deals").delete().eq("id", selected_deal_id).execute()
                        log_activity(st.session_state.user, f"Deleted Locked Deal Record ID: {selected_deal_id}")
                        st.warning("Deal record line removed.")
                        st.rerun()
                else:
                    st.write("No matching database dynamic ID key found to perform deletes.")
    else: 
        st.info("System Registry Dashboard khali hai.")

# -----------------------------
# 8. WORKING PROGRESS MODULE
# -----------------------------
elif st.session_state.current_nav == "Working Progress":
    st.title("📈 Staff Daily Progress Reports")
    try:
        logs = supabase.table("activity_logs").select("*").order("id", desc=True).execute().data
        if logs:
            df_progress = pd.DataFrame(logs)[["created_at", "user", "target_area", "action"]]
            df_progress.columns = ["Timestamp", "Staff Name", "Target Area Location", "Activity Details Logged"]
            pdf_html = convert_df_to_pdf_html(df_progress, "Staff Performance & Field Working Logs")
            st.download_button(label="📥 Print PDF (Download Working Reports)", data=pdf_html, file_name="staff_working_report.html", mime="text/html")
            st.dataframe(df_progress, use_container_width=True, hide_index=True)
        else: st.info("Koi working record data register nahi mila.")
    except Exception as e: st.error(f"Error fetching logs: {e}")

# -----------------------------
# 9. DEAL MATCHER, FINANCE & AUDIT LOGS
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
                budget, demand = client_record.get("max_budget", 0), client_record.get("demand_type")
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
    if st.session_state.role == "Viewer":
        try:
            acc_data = supabase.table("accounts").select("*").order("id", desc=True).execute().data
            if acc_data: st.dataframe(pd.DataFrame(acc_data), use_container_width=True, hide_index=True)
            else: st.info("Ledger records khali hain.")
        except: pass
    else:
        with st.form("fin"):
            t = st.selectbox("Type", ["Income", "Expense"])
            amt, desc = st.number_input("Amount", min_value=0), st.text_area("Remarks")
            if st.form_submit_button("Save Ledger Row"):
                supabase.table("accounts").insert({"type": t, "amount": amt, "description": desc, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}).execute()
                st.success("Recorded.")
                st.rerun()

elif st.session_state.current_nav == "Activity Logs":
    st.title("📋 Audit Activity Log System")
    try:
        logs = supabase.table("activity_logs").select("*").order("created_at", desc=True).execute().data
        if logs: st.dataframe(pd.DataFrame(logs)[["created_at", "user", "action", "target_area"]], use_container_width=True, hide_index=True)
    except: pass
