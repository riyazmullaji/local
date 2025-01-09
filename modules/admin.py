import streamlit as st
from utils.database import execute_query
from exception import CustomException
from logger import logging
import random
import pandas as pd

# Setup Logger
logger = logging.getLogger(__name__)

# Admin Dashboard
def admin_dashboard():
    st.title("🛠️ Admin Dashboard")

    try:
        # Fetch pending applications
        query = "FETCH_PENDING_APPLICATIONS"
        result = execute_query(query, ())

        if result:
            # Display pending applications in an interactive DataFrame
            st.markdown("### 📝 Pending Applications")
            df = pd.DataFrame(result, columns=["USERID", "Name", "District", "Aadhaar", "Income", "Application Status"])
            
            # Filter options
            district_filter = st.selectbox("Filter by District", options=["All"] + sorted(df["District"].unique()), index=0)
            filtered_df = df if district_filter == "All" else df[df["District"] == district_filter]

            # Display filtered results
            st.dataframe(filtered_df, use_container_width=True)

            # Extract the USERIDs from the filtered DataFrame
            user_ids = filtered_df["USERID"].tolist()

        else:
            st.info("No pending applications found.")
            user_ids = []  # No users available

    except CustomException as e:
        st.error(f"⚠️ Error fetching pending applications: {e}")
        logger.error(f"Error fetching pending applications: {e}")
        user_ids = []  # Handle errors by initializing an empty list

    # Divider for clarity
    st.markdown("---")

    # Verification Section
    st.markdown("### 🔍 Verify and Update Status")
    with st.form("verify_form"):
        # Dropdown for USERID
        user_id = st.selectbox("🔑 Select USERID to Verify", options=["Select a USERID"] + user_ids)
        district = st.text_input("🌍 Enter District", placeholder="Enter the district name")

        # Submit button within the form
        submitted = st.form_submit_button("Verify and Accept User")
        if submitted:
            if user_id != "Select a USERID" and district:
                try:
                    # Generate random Officer ID
                    officer_id = f"OFC{random.randint(100, 999)}"

                    # Update user status to "Accepted"
                    status_query = "UPDATE_USER_STATUS"
                    execute_query(status_query, (user_id, district))

                    # Assign Officer ID
                    officer_query = "UPDATE_USER_OFFICER_ID"
                    execute_query(officer_query, (officer_id, user_id))

                    # Update PMAY Data
                    update_query = "UPDATE_PMAY_DATA"
                    execute_query(update_query, (district,))

                    st.success(f"✅ User {user_id} from {district} has been verified and accepted.")
                    st.info(f"Officer ID **{officer_id}** assigned to the user.")
                    logger.info(f"User {user_id} verified and assigned Officer ID {officer_id}. PMAY data updated for {district}.")

                except CustomException as e:
                    st.error(f"⚠️ Error during verification: {e}")
                    logger.error(f"Verification error for {user_id}: {e}")
            else:
                st.warning("⚠️ Please select a valid USERID and enter the district.")
