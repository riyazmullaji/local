import streamlit as st
import pandas as pd
from utils.database import execute_query
from exception import CustomException
from logger import logging
import boto3
import os
import sys

# Setup Logger
logger = logging.getLogger(__name__)

# AWS S3 Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = "sanitation"
S3_REGION = "ap-south-1"

# Function to upload a file to S3
def upload_file_to_s3(file, user_id):
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=S3_REGION,
        )
        # Generate a unique file name
        file_name = f"{user_id}_sanitation_photo.jpg"
        # Upload file to S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            file_name,
            ExtraArgs={"ACL": "public-read"},  # Make the file publicly readable
        )
        # Construct the file URL
        file_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{file_name}"
        return file_url
    except Exception as e:
        raise CustomException(f"Error uploading file to S3: {str(e)}", sys)

# Function to fetch users with completed verification
def sanitation_verification():
    st.title("🚰 Sanitation Verification")

    # Information Banner
    st.info(
        """
        **Instructions:**
        - This page is for verifying sanitation status for users whose housing progress is marked as **Completed**.
        - Upload sanitation photos, and this will update both user and PMAY progress records.
        """
    )

    try:
        # Fetch users with completed verification from the database
        query = "FETCH_USERS_WITH_COMPLETEDVERF"
        result = execute_query(query, ())

        if not result:
            st.info("✅ No users pending sanitation verification.")
            return

        # Load data into a DataFrame
        columns = ["User ID", "Name", "District", "Aadhaar Number", "Income", "Completed Verification"]
        sanitation_df = pd.DataFrame(result, columns=columns)

        # Filter users by district
        st.markdown("### 🔍 Filter Users")
        district_filter = st.selectbox(
            "Filter by District",
            options=["All"] + sorted(sanitation_df["District"].unique()),
            index=0
        )
        filtered_df = (
            sanitation_df if district_filter == "All" else sanitation_df[sanitation_df["District"] == district_filter]
        )

        # Display filtered users
        st.markdown("### 📋 Users Pending Sanitation Verification")
        st.dataframe(filtered_df, use_container_width=True)

        # Dropdown to select a user
        user_id = st.selectbox(
            "🔑 Select User ID for Sanitation Verification",
            options=["Select User ID"] + filtered_df["User ID"].tolist(),
            help="Select a User ID to verify sanitation status."
        )

        if user_id == "Select User ID":
            return

        # Get the district for the selected user
        selected_district = filtered_df.loc[filtered_df["User ID"] == user_id, "District"].values[0]

    except CustomException as e:
        st.error(f"⚠️ Error fetching users: {e}")
        logger.error(f"Error fetching users: {e}")
        return

    # Divider for clarity
    st.markdown("---")

    # Sanitation Verification Form
    st.markdown("### 🛠️ Sanitation Verification Form")
    with st.form(key="sanitation_form"):
        # Upload File
        uploaded_file = st.file_uploader(
            "📸 Upload Sanitation Photo", 
            type=["jpg", "jpeg", "png"], 
            help="Upload a photo as proof of sanitation."
        )

        # Submit Button
        submitted = st.form_submit_button("✅ Submit Verification")

        if submitted:
            if not uploaded_file:
                st.error("⚠️ Please upload a sanitation photo!")
                return

            try:
                # Upload sanitation photo to S3
                sanitation_url = upload_file_to_s3(uploaded_file, user_id)

                # Update the database
                try:
                    # Update sanitation URL in the user table
                    execute_query("UPDATE_USER_SANITATION_URL", (sanitation_url, user_id))

                    # Update PMAY progress in the PMAY table
                    execute_query("UPDATE_PMARY_PROGRESS_COMPLETED", (selected_district,))

                    # Success message
                    st.success(f"✅ Sanitation verification successfully updated for User ID: {user_id}")
                    logger.info(f"Sanitation verification updated for User ID: {user_id}, District: {selected_district}")

                except CustomException as e:
                    st.error(f"⚠️ Error updating database: {e}")
                    logger.error(f"Error updating database: {e}")

            except CustomException as e:
                st.error(f"⚠️ Error uploading file to S3: {e}")
                logger.error(f"Error uploading file to S3: {e}")
