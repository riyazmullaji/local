import streamlit as st
from logger import logging  
from exception import CustomException  
from utils.database import execute_query  
import pandas as pd
import matplotlib.pyplot as plt

# Header Section with Styled Title
def header_section():
    # Styled Title
    st.markdown(
        """
        <h1 style="text-align:center; font-size: 50px; font-weight: bold; font-family: 'Verdana';">
                <span style="color: red;">PMAY</span>
                <span style="color: white;"> Housing & Sanitation Tracker</span>
            </h1>
        """, unsafe_allow_html=True)
    
    # Subheading with Custom Style
    st.markdown(
        """
        <h3 style="text-align:center; color: #6A5ACD; font-size: 20px; font-style: italic;">
            Empowering Communities with Homes and Sanitation for a Healthier Tomorrow.
        </h3>
        """, unsafe_allow_html=True)
    
    st.image("assets/banner.jpg", use_container_width=True)

# Home Module with Tab Navigation and Layout
def home_module():
    try:
        header_section()  # Display header with title and subheading

        # Create Tabs for navigation
        tab = st.radio("Analyzing the performance of PMAY",["Overview", "Performance Rankings", "District stats"], horizontal=True)

        if tab == "Overview":
            st.markdown("### Overview: Key Metrics")
            overview_metrics()

        elif tab == "Performance Rankings":
            st.markdown("### 📊 District Rankings")
            performance_ranking()

        elif tab == "District stats":
            st.markdown("### 🆚 District Stats")
            district = st.selectbox("Select a District", ["Bagalkot", "Ballari", "Belagavi", "Bengaluru_Urban", 
                                                        "Chikkamagaluru", "Hassan", "Kodagu", "Mysuru", "Raichur", 
                                                        "Shivamogga", "Tumakuru", "UttaraKannada"])
            district_plot(district)

    except CustomException as ce:
        logging.error(f"Custom Exception in Home Module: {ce}")
        st.error("An error occurred while loading the home module. Please try again later.")
    except Exception as e:
        logging.error(f"Unexpected Error in Home Module: {e}")
        st.error("An unexpected error occurred. Please check the logs.")

# Overview: Key Metrics
def overview_metrics():
    try:
        # Fetch data for the metrics
        total_beneficiaries = execute_query("FETCH_TOTAL_BENEFICIARIES")[0][0]
        total_completed = execute_query("FETCH_COMPLETED_HOMES")[0][0]
        total_unstarted = execute_query("FETCH_UNSTARTED_PROJECTS")[0][0]
        stage_progress = execute_query("FETCH_STAGE_PROGRESS")[0]

        # Display metrics in a dashboard style
        col1, col2 = st.columns(2)
        col1.metric("👥 Total Beneficiaries", f"{total_beneficiaries:,}", help="The total number of households that have been identified as beneficiaries under the PMAY scheme.")
        col2.metric("🏡 Completed Homes", f"{total_completed:,}", help="The number of homes that have been fully constructed and handed over to beneficiaries.")

        col3, col4 = st.columns(2)
        col3.metric("🚧 Unstarted Projects", f"{total_unstarted:,}", help="The number of housing projects that have not yet started construction.")

        # Stage Progress Section
        st.markdown("### 🔨 Stage Progress Overview")
        st.markdown("""
            The following bar chart illustrates the progress at various stages of housing construction. 
            This includes the **Foundation**, **Lintel**, and **Roof** stages. 
            A higher bar indicates greater completion at that stage.
        """)

        # Create a DataFrame for stage progress to display it in a bar chart
        progress_data = {
            "Foundation": stage_progress[0],
            "Lintel": stage_progress[1],
            "Roof": stage_progress[2],
        }

        # Convert data into a pandas DataFrame for better visualization
        stage_df = pd.DataFrame(list(progress_data.items()), columns=["Stage", "Units"])

        # Create a custom stacked bar chart with color gradients
        fig, ax = plt.subplots(figsize=(8, 6))

        # Set custom colors (using color gradients for better visual appeal)
        ax.bar(stage_df["Stage"], stage_df["Units"], color=['#ADD8E6', '#90EE90', '#FFCC99'], width=0.6)

        # Set title and labels with larger fonts
        ax.set_title("Stage Progress", fontsize=18, fontweight='bold')
        ax.set_xlabel("Stage of Construction", fontsize=14)
        ax.set_ylabel("Units Completed", fontsize=14)

        # Add percentages on top of the bars for clarity
        for i, value in enumerate(stage_df["Units"]):
            ax.text(i, value + 2, f"{value} ({value/total_beneficiaries*100:.1f}%)", ha='center', va='bottom', fontsize=12)

        # Customize tick params
        ax.tick_params(axis='x', colors='black')
        ax.tick_params(axis='y', colors='black')

        # Set background color and gridlines for contrast
        ax.set_facecolor('#000000')
        ax.grid(True, axis='y', linestyle='--', alpha=0.6)

        # Display stage progress textually with clearer presentation
        st.markdown(f"#### 🚧 **Foundation Stage:** <span style='color:#FF6F61; font-size: 20px; font-weight: bold;'>{stage_progress[0]:,} units</span>", unsafe_allow_html=True)
        st.markdown(f"#### 🏗️ **Lintel Stage:** <span style='color:#FFD700; font-size: 20px; font-weight: bold;'>{stage_progress[1]:,} units</span>", unsafe_allow_html=True)
        st.markdown(f"#### 🏠 **Roof Stage:** <span style='color:#32CD32; font-size: 20px; font-weight: bold;'>{stage_progress[2]:,} units</span>", unsafe_allow_html=True)

        # Display the bar chart in Streamlit
        st.pyplot(fig)

        # Provide a summary of the progress
        st.markdown("### 📝 Summary")
        st.markdown(f"""
        - **Foundation Stage**: {stage_progress[0]} units completed.
        - **Lintel Stage**: {stage_progress[1]} units completed.
        - **Roof Stage**: {stage_progress[2]} units completed.

        The project is progressing steadily, with a notable increase in the number of homes reaching the lintel and roof stages.
        This indicates a reduction in the time taken per home construction. Efforts to speed up the foundation stage are still ongoing.
        """)

        logging.info("Overview metrics loaded successfully.")

        # Footer for feedback on unlawful practices
        st.markdown("---")
        st.markdown("""
            ## ⚖️ Report Unlawful Practices
            If you suspect any unlawful practices or discrepancies in the housing project, please report them by providing feedback below. Your input is invaluable to ensure transparency and accountability.
        """)
        
        with st.form("complaint_form"):
            complaint_text = st.text_area("Please share your complaint here:", height=100)
            submit_button = st.form_submit_button("Submit Complaint")
            
            if submit_button and complaint_text:
                # Update the complaint in the database
                query = "UPDATE_COMPLAINT"
                execute_query(query, complaint_text)
                st.success("Thank you for your complaint! It will be reviewed promptly.")

    except Exception as e:
        st.error(f"Error loading Overview Metrics: {e}")
        logging.error(f"Error loading Overview Metrics: {e}")


# Performance Ranking
def performance_ranking():
    try:
        # Fetch district rankings
        rankings = execute_query("FETCH_PERFORMANCE_RANKING")
        if rankings:
            # Convert query result to a Pandas DataFrame with appropriate column names
            rankings_df = pd.DataFrame(rankings, columns=["District", "Completion Rate (%)"])

            # Title for the section
            st.markdown("<h3 style='text-align:center; color:#FF6F61;'>🏆 Performance Rankings</h3>", unsafe_allow_html=True)

            # Display top performing district in a styled card
            top_district = rankings_df.iloc[0]
            st.markdown("""
                <div style="background-color:#00bfae; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <h4 style="color: white; text-align: center;">Top Performing District</h4>
                    <h3 style="color: white; text-align: center;">{}: <span style="color: #ffeb3b;">{:.2f}%</span></h3>
                </div>
            """.format(top_district["District"], top_district["Completion Rate (%)"]), unsafe_allow_html=True)

            # Display least performing district in a styled card
            least_district = rankings_df.iloc[-1]
            st.markdown("""
                <div style="background-color:#ff6666; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <h4 style="color: white; text-align: center;">Least Performing District</h4>
                    <h3 style="color: white; text-align: center;">{}: <span style="color: #ffeb3b;">{:.2f}%</span></h3>
                </div>
            """.format(least_district["District"], least_district["Completion Rate (%)"]), unsafe_allow_html=True)

            # Full ranking table (with table styling)
            st.markdown("#### 📝 Full District Rankings", unsafe_allow_html=True)
            st.dataframe(rankings_df.style.applymap(lambda x: 'background-color: #FFEB3B' if isinstance(x, (int, float)) and x < 50 else '', subset=["Completion Rate (%)"]))

        else:
            st.error("No performance ranking data found.")
    except Exception as e:
        st.error(f"Error loading performance rankings: {e}")
        logging.error(f"Error loading performance rankings: {e}")

# District Comparison Plot
def district_plot(district):
    try:
        query_params = (district,)
        district_data = execute_query("FETCH_DISTRICT_DATA", query_params)

        # Check if data was fetched successfully
        if district_data:
            # Convert query result to a Pandas DataFrame
            district_df = pd.DataFrame(district_data, columns=["District", "Foundation", "Lintel", "Roof", "Completed"])
            
            # Extract values for plotting
            foundation = district_df.iloc[0]["Foundation"]
            lintel = district_df.iloc[0]["Lintel"]
            roof = district_df.iloc[0]["Roof"]
            completed = district_df.iloc[0]["Completed"]

            # Create a bar plot with black background
            plt.style.use('dark_background')  # Set the background color to black

            plt.figure(figsize=(8, 6))
            bars = plt.bar(
                ["Foundation", "Lintel", "Roof", "Completed"], 
                [foundation, lintel, roof, completed], 
                color=['skyblue', 'green', 'orange', 'purple']
            )
            
            # Add numbers on top of each bar
            for bar in bars:
                yval = bar.get_height()
                plt.text(
                    bar.get_x() + bar.get_width() / 2,  # X position of text (center of the bar)
                    yval + 1,  # Y position of text (above the bar)
                    str(int(yval)),  # Value to display (int value)
                    ha='center',  # Horizontal alignment
                    color='white',  # Text color
                    fontsize=12,  # Text size
                    fontweight='bold'  # Make the text bold for better visibility
                )

            # Customize the title and labels to have white text
            plt.title(f"PMAY Housing Progress for {district}", fontsize=14, color='white')
            plt.xlabel("Progress Stages", fontsize=12, color='white')
            plt.ylabel("Number of Units", fontsize=12, color='white')
            
            # Change the color of the tick labels to white
            plt.xticks(color='white')
            plt.yticks(color='white')

            plt.tight_layout()
            
            # Show the plot in Streamlit
            st.pyplot(plt)
            logging.info(f"District plot generated successfully for {district}")
        else:
            st.warning(f"No data found for district: {district}")
            logging.warning(f"No data found for district: {district}")

    except Exception as e:
        st.error(f"Error fetching or plotting data for district: {district}")
        logging.error(f"Error fetching or plotting data for district: {district} | Error: {e}")
        raise CustomException(f"Error fetching or plotting data for district: {district}", str(e))
if __name__ == "__main__":
    home_module()
