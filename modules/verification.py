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
def upload_to_s3(file, file_name):
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=S3_REGION,
        )
        s3_client.upload_fileobj(
            file,
            S3_BUCKET_NAME,
            file_name,
            ExtraArgs={"ACL": "public-read"},
        )
        file_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{file_name}"
        return file_url
    except Exception as e:
        raise CustomException(f"Error uploading file to S3: {str(e)}", sys)

# Function to verify user progress
def verify_user_progress():
    st.title("📜 Verify User Progress")

    # Info Section
    st.info(
        """
        **Important Information:**
        - Verified progress updates will be synced with the official PMAY data.
        - If the progress is marked as **Completed**, it requires sanitation verification before final approval. 
          Please navigate to the **Sanitation Page** for uploading the necessary images after this step.
        """
    )
    st.markdown("---")

    # Fetch users with progress not started
    try:
        query = "FETCH_PROGRESS_NOT_STARTED"
        result = execute_query(query, ())

        if result:
            # Define the column names for the result
            columns = ["User ID", "Name", "District", "Officer ID", "Progress Stage"]
            progress_df = pd.DataFrame(result, columns=columns)
            
            # Display the data in a collapsible section
            with st.expander("👥 View Pending Progress Updates", expanded=True):
                district_filter = st.selectbox(
                    "Filter by District", 
                    options=["All"] + sorted(progress_df["District"].unique()), 
                    index=0
                )
                filtered_df = (
                    progress_df if district_filter == "All" else progress_df[progress_df["District"] == district_filter]
                )
                st.dataframe(filtered_df, use_container_width=True)
            
            # Dropdown for selecting a user
            user_id = st.selectbox(
                "🔑 Select User ID for Verification", 
                options=["Select User ID"] + filtered_df["User ID"].tolist(),
                help="Select the User ID you want to verify."
            )
        else:
            st.info("✅ No users with pending progress updates found.")
            return
    except CustomException as e:
        st.error(f"⚠️ Error fetching users: {e}")
        logger.error(f"Error fetching users: {e}")
        return

    # Divider for clarity
    st.markdown("---")

    # Verification Form
    st.markdown("### 🛠️ Verification Form")
    with st.form(key="verification_form"):
        # Officer ID
        officer_id = st.text_input(
            "🆔 Officer ID", 
            placeholder="Enter Officer ID responsible for verification",
            help="Provide the Officer ID assigned to the verification task."
        )
        
        # Progress Stage Dropdown
        progress_stage = st.selectbox(
            "🏗️ Select Progress Stage",
            ["", "FOUNDATION", "LINTEL", "ROOF", "COMPLETED"],
            help="Select the current progress stage of the beneficiary."
        )

        # File Uploader
        uploaded_file = st.file_uploader(
            "📸 Upload Verification Photo", 
            type=["jpg", "jpeg", "png"], 
            help="Upload a photo as proof for the selected progress stage."
        )

        # Submit Button
        submitted = st.form_submit_button("✅ Submit Verification")

        if submitted:
            # Validation
            if not (officer_id and progress_stage and user_id):
                st.error("⚠️ All fields are required! Please fill in all details.")
                return

            if uploaded_file is None:
                st.error("⚠️ Please upload a verification photo!")
                return

            # Generate a unique file name
            file_name = f"{user_id}_{progress_stage.lower()}_photo.jpg"

            try:
                # Upload the photo to S3 and get the file URL
                file_url = upload_to_s3(uploaded_file, file_name)

                # Update progress stage in the database
                try:
                    if progress_stage == "FOUNDATION":
                        execute_query("UPDATE_PMARY_PROGRESS_FOUNDATION", (filtered_df.loc[filtered_df["User ID"] == user_id, "District"].values[0],))
                        execute_query("UPDATE_USER_FOUNDATION_URL", (file_url, user_id))
                    elif progress_stage == "LINTEL":
                        execute_query("UPDATE_PMARY_PROGRESS_LINTEL", (filtered_df.loc[filtered_df["User ID"] == user_id, "District"].values[0],))
                        execute_query("UPDATE_USER_LINTEL_URL", (file_url, user_id))
                    elif progress_stage == "ROOF":
                        execute_query("UPDATE_PMARY_PROGRESS_ROOF", (filtered_df.loc[filtered_df["User ID"] == user_id, "District"].values[0],))
                        execute_query("UPDATE_USER_ROOF_URL", (file_url, user_id))
                    elif progress_stage == "COMPLETED":
                        execute_query("UPDATE_PMARY_PROGRESS_COMPLETED", (filtered_df.loc[filtered_df["User ID"] == user_id, "District"].values[0],))
                        execute_query("UPDATE_USER_COMPLETED_URL", (file_url, user_id))

                        # Redirect to sanitation page
                        st.success(f"✅ Completed verification updated for User ID: {user_id}. Redirecting to the sanitation page...")
                        st.markdown("[Go to Sanitation Page](#sanitation-page)", unsafe_allow_html=True)
                        return

                    st.success(f"✅ {progress_stage} verification successfully updated for User ID: {user_id}.")
                    st.info(f"Photo uploaded to: {file_url}")
                    logger.info(f"{progress_stage} verification updated for User ID: {user_id}. Photo URL: {file_url}")

                except CustomException as e:
                    st.error(f"⚠️ Error updating database: {e}")
                    logger.error(f"Error updating database: {e}")

            except CustomException as e:
                st.error(f"⚠️ Error uploading file to S3: {e}")
                logger.error(f"Error uploading file to S3: {e}")
