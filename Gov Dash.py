import streamlit as st

def main():
    # Set page configuration for a professional layout
    st.set_page_config(page_title="Government Dashboard", layout="wide")

    # Title with an emoji for visual appeal
    st.title("🏛️ Government Dashboard")

    # Introduction Section
    st.markdown("""
    Welcome to the **Government Dashboard**! This application provides insights into various government datasets, helping you access and analyze information effortlessly.

    ## Available Modules

    ### 1. Consumption of Petroleum Products
    📈 **Analyze** the monthly consumption of different petroleum products.  
    **Use Cases:**
    - "Show me the consumption of LPG in 2022."
    - "I want the monthly consumption of ATF in March 2023."

    ### 2. Air Sewa
    ✈️ **Access** information related to aviation grievances, flight schedules, FAQs, and airport services.  
    **Use Cases:**
    - "Show me the aviation grievances for Ethiopian Airlines in 2024."
    - "What is the flight schedule for IndiGo flight 451 from Bengaluru to Lucknow?"
    - "I have a question about Jet Airways baggage services."
    - "Where are the pharmacy services at Mumbai Airport?"

    ## How to Navigate

    Use the **sidebar** on the left to navigate between the available modules. Click on the module name to access its features and start your query.

    ## Features

    - **Natural Language Queries**: Enter your questions in natural language, and the system will parse and retrieve relevant data.
    - **Interactive DataFrames**: View results in organized tables and download them as CSV files.
    - **Assistance for Unsupported Queries**: Receive helpful guidance if your query doesn't match available datasets.

    ## Security

    - **Secure API Keys**: All API keys are securely stored using Streamlit's Secrets Management, ensuring your sensitive information remains protected.

    ## Contact

    For any support or feedback, please contact the development team at [support@govdash.com](mailto:support@govdash.com).
    """)

    # Visual Representation of Modules using Columns
    st.markdown("## Quick Access to Modules")

    col1, col2 = st.columns(2)

    with col1:
        st.image("https://img.icons8.com/fluency/96/000000/oil-industry.png", width=100)
        st.header("Consumption of Petroleum Products")
        st.markdown("""
        📈 **Analyze** the monthly consumption of different petroleum products.  
        **Start Now:** Enter your query in the sidebar.
        """)

    with col2:
        st.image("https://img.icons8.com/fluency/96/000000/aircraft-take-off.png", width=100)
        st.header("Air Sewa")
        st.markdown("""
        ✈️ **Access** information related to aviation grievances, flight schedules, FAQs, and airport services.  
        **Start Now:** Enter your query in the sidebar.
        """)

    # Footer Section
    st.markdown("""
    ---
    **Government Dashboard - Created by Data Scientist Mohd Amaan** | © 2025 All Rights Reserved.
    """)

if __name__ == "__main__":
    main()
