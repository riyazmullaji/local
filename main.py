import streamlit as st
from utils.database import execute_query
from exception import CustomException
import logging
import pandas as pd

# Initialize logger
logger = logging.getLogger(__name__)

def main():
    # Example: Get the district name from Streamlit user input or use hardcoded value
    district_name = st.selectbox("Select District", ["Bagalkot", "Ballari", "Belagavi"])  # Example list

    try:
        # Define the query and pass the district as a parameter (dictionary)
        query = "FETCH_DISTRICT_DATA"
        params = district_name  # Pass district as a dictionary with key "district"
        result = execute_query(query, params)

        # Show the result as a DataFrame in Streamlit
        if result:
            df = pd.DataFrame(result, columns=["DISTRICT", "FOUNDATION", "LINTEL", "ROOF", "COMPLETED"])
            st.write(df)

        else:
            st.error("No data found for the selected district")

    except CustomException as e:
        logger.error(f"Error fetching data for district {district_name}: {e}")
        st.error(f"Error fetching data for district {district_name}: {e}")

if __name__ == "__main__":
    main()
