import streamlit as st
from utils.database import execute_query
from logger import logger
from exception import CustomException  # Assuming CustomException is defined in exception.py

# Update Project Progress
def update_module():
    st.title("🏗️ Update Project Progress")
    st.markdown(
        """
        Welcome to the **PMAY Progress Update Portal**.  
        Kindly update the current stage of your project.  
        After submission, **our officials will visit your site for verification and photo documentation**.  
        Thank you for your cooperation!
        """
    )

    # Separator for better visuals
    st.markdown("---")

    # Input fields
    name = st.text_input("🔤 Full Name", placeholder="Enter your full name")
    aadhaar = st.text_input(
        "🔢 Aadhaar Number", 
        placeholder="Enter your 12-digit Aadhaar number", 
        type="password"
    )
    progress_stage = st.selectbox(
        "🔄 Select Progress Stage", 
        ["Foundation", "Lintel", "Roof", "Completed"], 
        help="Choose the current stage of your project"
    )

    # Aadhaar validation and masking
    aadhaar_valid = len(aadhaar) == 12 and aadhaar.isdigit()
    if aadhaar and not aadhaar_valid:
        st.error("Aadhaar number must be exactly 12 digits and contain only numbers.")
    
    # Submit button
    if st.button("Submit Progress Update"):
        if not (name and aadhaar and progress_stage):
            st.error("🚫 All fields are required. Please fill in Name, Aadhaar, and Progress Stage.")
            logger.warning("Update failed: Missing fields.")
        elif not aadhaar_valid:
            st.error("🚫 Invalid Aadhaar number! Please ensure it is 12 digits.")
            logger.warning("Update failed: Invalid Aadhaar number.")
        else:
            try:
                # Fetch the user ID based on Name and Aadhaar
                fetch_user_query = "FETCH_USERID_QUERY"
                result = execute_query(fetch_user_query, (name, aadhaar))

                if result:  # If user exists
                    user_id = result[0][0]  # Extract the user ID

                    # Update the progress stage
                    update_query = "UPDATE_USER_PROJECT_PROGRESS"
                    execute_query(update_query, (progress_stage, user_id))

                    # Success message
                    st.success(
                        f"🎉 Project progress for **{name}** updated to **{progress_stage}**.\n"
                        "An official will visit your site soon for verification."
                    )
                    logger.info(
                        f"Successfully updated progress to {progress_stage} for user ID: {user_id} ({name})."
                    )
                else:
                    st.error("❌ No user found with the provided Name and Aadhaar.")
                    logger.error(f"No user found with Name: {name} and Aadhaar: {aadhaar}")

            except CustomException as e:
                st.error(f"⚠️ Error: {e}")
                logger.error(f"Custom exception during progress update: {e}")

            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {e}")
                logger.error(f"Unexpected error during progress update: {e}")

    # Separator for footer
    st.markdown("---")

    # Footer information
    st.info(
        "📌 **Important:** Ensure that your Aadhaar number and project details are accurate. "
        "Verification may take 7-10 business days."
    )
