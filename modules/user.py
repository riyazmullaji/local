import streamlit as st
from utils.database import execute_query
import uuid
from exception import CustomException
from logger import logging

# Set up logger
logger = logging.getLogger(__name__)

# Registration Form
def register_user():
    st.title("📝 Register New Beneficiary")
    st.markdown("Please fill out the form below to register for the PMAY scheme.")

    # User input fields
    name = st.text_input("Full Name", placeholder="Enter your full name")
    aadhaar = st.text_input(
        "Aadhaar Number",
        placeholder="Enter your 12-digit Aadhaar Number",
        type="password"
    )
    income = st.number_input(
        "Annual Income (₹)",
        min_value=10000,
        max_value=1000000,
        value=50000,
        step=1000,
        help="Enter your annual income between ₹10,000 and ₹10,00,000"
    )

    # District selection with a search-friendly list
    district = st.selectbox(
        "District",
        options=[
            "Bagalkot", "Ballari", "Belagavi", "Bengaluru Rural", "Bengaluru Urban", "Bidar",
            "Chamarajanagar", "Chikkaballapur", "Chikkamagaluru", "Chitradurga", "Dakshinakannada",
            "Davanagere", "Dharwad", "Gadag", "Hassan", "Haveri", "Kalaburagi", "Kodagu", "Kolar",
            "Koppal", "Mandya", "Mysuru", "Raichur", "Ramanagara", "Shivamogga", "Tumakuru", "Udupi",
            "Uttarakannada", "Vijayanagara", "Vijayapura", "Yadgiri"
        ],
        help="Select your district from the dropdown list"
    )

    # Real-time validation for Aadhaar Number
    aadhaar_valid = len(aadhaar) == 12 and aadhaar.isdigit()
    if aadhaar and not aadhaar_valid:
        st.error("Aadhaar number must be exactly 12 digits and contain only numbers.")

    # Handle registration logic
    if st.button("Register"):
        if not (name and aadhaar and income and district):
            st.error("🚫 All fields are required! Please fill in all the details.")
            logger.warning("Registration attempt failed due to missing fields.")
        elif not aadhaar_valid:
            st.error("🚫 Invalid Aadhaar Number! Please ensure it is 12 digits.")
            logger.warning("Registration attempt failed due to invalid Aadhaar number.")
        else:
            user_id = str(uuid.uuid4())  # Generate a unique ID for the user
            query = "INSERT_USER_APPLICATION"  # Query name from queries.sql

            # Confirmation step before final submission
            try:
                # Execute the query to insert the new user data
                execute_query(query, (user_id, name, district, aadhaar, income))
                st.success(f"🎉 Registration successful! Your application ID is **{user_id}**.")
                logger.info(f"User registered successfully with ID: {user_id}")
            except CustomException as e:
                st.error(f"❌ Error during registration: {e}")
                logger.error(f"Error during registration for user {user_id}: {e}")
