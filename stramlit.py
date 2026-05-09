import streamlit as st
from supabase import create_client

# Supabase setup (pehle se mojud hai)
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def manage_inventory():
    st.title("📋 Office Inventory (Edit/Delete)")

    # 1. Search and Filter
    search_query = st.text_input("🔍 Search by Area or Owner", "").lower()
    
    # Database se data lana
    response = supabase.table("inventory").select("*").order("created_at", desc=True).execute()
    data = response.data

    if not data:
        st.warning("Inventory khali hai!")
        return

    for item in data:
        # Search Filter Logic
        if search_query in item['area'].lower() or search_query in item['owner_name'].lower():
            
            # Har property ke liye ek alag card (Expander)
            with st.expander(f"📍 {item['area']} | {item['property_type']} | {item['price']} PKR"):
                
                # Layout for Details
                col1, col2, col3 = st.columns(3)
                col1.write(f"**Beds:** {item['beds']}")
                col2.write(f"**Size:** {item['marla']} Marla")
                col3.write(f"**Portion:** {item['portion']}")
                
                st.write(f"**Owner:** {item['owner_name']} ({item['owner_contact']})")
                st.write(f"**Status:** {item['status']}")

                # --- EDIT & DELETE BUTTONS ---
                btn_col1, btn_col2 = st.columns(2)

                # A. EDIT OPTION
                if btn_col1.button("✏️ Edit Property", key=f"edit_{item['id']}"):
                    st.session_state[f"editing_{item['id']}"] = True

                # B. DELETE OPTION
                if btn_col2.button("🗑️ Delete Record", key=f"del_{item['id']}"):
                    # Confirmation check
                    st.error(f"Kya aap waqai is property ko delete karna chahte hain?")
                    if st.button("Haan, Pakka Delete Karein!", key=f"confirm_{item['id']}"):
                        supabase.table("inventory").delete().eq("id", item['id']).execute()
                        st.success("Record delete ho gaya! Refresh karein.")
                        st.rerun()

                # --- EDIT FORM (Sirf tab khulega jab Edit par click hoga) ---
                if st.session_state.get(f"editing_{item['id']}", False):
                    with st.form(f"form_edit_{item['id']}"):
                        st.subheader("Update Details")
                        new_price = st.number_input("New Price", value=float(item['price']))
                        new_status = st.selectbox("Status", ["Available", "Sold", "Rented"], index=["Available", "Sold", "Rented"].index(item['status']))
                        new_note = st.text_area("Staff Notes", value=item.get('visiting_time', ""))
                        
                        save_btn = st.form_submit_button("✅ Update Now")
                        if save_btn:
                            supabase.table("inventory").update({
                                "price": new_price,
                                "status": new_status,
                                "visiting_time": new_note
                            }).eq("id", item['id']).execute()
                            
                            st.session_state[f"editing_{item['id']}"] = False
                            st.success("Data update ho gaya!")
                            st.rerun()

# Ise main menu mein call karein
if choice == "📋 View Inventory":
    manage_inventory()