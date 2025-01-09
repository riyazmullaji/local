import streamlit as st
from modules.home import home_module
from modules.user import register_user
from modules.update import update_module
from modules.admin import admin_dashboard
from modules.verification import verify_user_progress
from modules.sanitation import sanitation_verification

# Application Title
st.set_page_config(page_title="PMAY Dashboard", layout="wide", page_icon="🏠")

# Sidebar for Navigation
st.sidebar.title("📂 **Navigation**")
app_mode = st.sidebar.radio(
    "Choose a Section:",
    options=[
        "🏡 Home",
        "📝 Register for scheme",
        "📈 Update Housing Progress",
        "🔑 Admin Dashboard",
        "🔍 Verify Beneficiary Progress",
        "🚰 Sanitation Verification"
    ],
    help="Navigate to the desired section of the dashboard."
)

# Conditional rendering based on the navigation choice
if app_mode == "🏡 Home":
    home_module()  # Home page functionality
elif app_mode == "📝 Register for scheme":
    register_user()  # Registration functionality
elif app_mode == "📈 Update Housing Progress":
    update_module()  # Update Progress functionality
elif app_mode == "🔑 Admin Dashboard":
    admin_dashboard()  # Admin Dashboard functionality
elif app_mode == "🔍 Verify Beneficiary Progress":
    verify_user_progress()  # Verification functionality
elif app_mode == "🚰 Sanitation Verification":
    sanitation_verification()  # Sanitation verification functionality
else:
    st.error("🚫 **Invalid Selection! Please choose a valid section from the navigation menu.**")
