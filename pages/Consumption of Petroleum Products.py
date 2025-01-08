import streamlit as st
import requests
import re
import io
import pandas as pd

################################################################################
# 1. Define API Information
################################################################################

API_INFO = {
    "consumption_petroleum": {
        "name": "Consumption of Petroleum Products",
        "endpoint": "https://api.data.gov.in/resource/7b624b4a-1456-4945-80d0-dfb5e40ddcff",
        "filters": ["_month_", "year", "products", "quantity_000_metric_tonnes_", "updated_date"],
        "columns": [
            "month", "year", "products", "quantity_000_metric_tonnes_", "updated_date"
        ]
    }
}

################################################################################
# 2. API Call Function
################################################################################

def call_api(api_identifier, filters, format_type="csv"):
    """
    Calls the specified API with the provided filters and returns the response.
    
    Parameters:
        api_identifier (str): Identifier for the API to call.
        filters (dict): Dictionary of filters to apply.
        format_type (str): Response format ('csv' or 'json'). Defaults to 'csv'.
        
    Returns:
        dict: Contains filters used, response data, and any messages.
    """
    # Map API identifiers to their respective API keys from secrets
    api_key_mapping = {
        "consumption_petroleum": st.secrets["PETROLEUM_API_KEY"]
    }

    api_key = api_key_mapping.get(api_identifier)
    if not api_key:
        return {"error": "API key not found for the selected API."}

    api = API_INFO.get(api_identifier)
    if not api:
        return {"error": "Invalid API identifier."}
    
    url = api["endpoint"]
    params = {
        "api-key": api_key,
        "format": format_type,
        "offset": filters.get("offset", 0),
        "limit": filters.get("limit", 15)  # Default limit set to 15 as per your code
    }
    
    # Add relevant filters
    for filter_key in api["filters"]:
        if filters.get(filter_key):
            params[f"filters[{filter_key}]"] = filters[filter_key]
    
    response = requests.get(url, params=params)
    
    result = {
        "filters_used": filters,
        "response_data": [],
        "message": ""
    }
    
    if response.status_code == 200:
        if format_type == "csv":
            try:
                df = pd.read_csv(io.StringIO(response.text))
                result["response_data"] = df.to_dict(orient="records")
                if df.empty:
                    result["message"] = "No data found for the given filters."
            except Exception as e:
                result["message"] = f"Failed to parse CSV data: {e}"
        else:
            try:
                data = response.json()
                records = data.get("records", [])
                result["response_data"] = records
                if not records:
                    result["message"] = "No data found for the given filters."
            except Exception as e:
                result["message"] = f"Failed to parse JSON data: {e}"
    else:
        result["message"] = f"Request failed with status code {response.status_code}."
    
    return result

################################################################################
# 3. Query Classification Function
################################################################################

def classify_query(query):
    """
    Determine if the query pertains to Petroleum Consumption API.
    Since there's only one API in this module, it returns the identifier if relevant keywords are found.
    
    Returns:
        str or None: API identifier or None if no match is found.
    """
    query_lower = query.lower()
    keywords = ["consumption", "petroleum", "lpg", "atf", "hsd", "sko", "naphtha", "bitumen", "fo & lshs"]

    if any(keyword in query_lower for keyword in keywords):
        return "consumption_petroleum"
    
    return None

################################################################################
# 4. Filter Parsing Function
################################################################################

def parse_filters_petroleum(query):
    """
    Parse filters specific to the Consumption of Petroleum Products API.
    """
    filters = {
        "offset": 0,
        "limit": 15,  # Default limit as per your original code
        "format": "csv"  # Always CSV for consistency
    }

    # Basic month detection
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    for m in months:
        if m.lower() in query.lower():
            filters["month"] = m
            break

    # Basic year detection (4 digits)
    match_year = re.search(r'\b\d{4}\b', query)
    if match_year:
        filters["year"] = match_year.group()

    # Basic products detection
    possible_products = ["LPG", "ATF", "HSD", "SKO", "Naphtha",
                         "Bitumen", "Others", "FO & LSHS"]
    for product in possible_products:
        if product.lower() in query.lower():
            filters["products"] = product
            break

    # Quantity detection (if applicable, based on your API's capabilities)
    match_quantity = re.search(r'quantity\s*[:\-]?\s*(\d+)', query.lower())
    if match_quantity:
        filters["quantity_000_metric_tonnes_"] = match_quantity.group(1)

    # Updated date detection (if applicable)
    match_updated_date = re.search(r'updated\s*date\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})', query.lower())
    if match_updated_date:
        filters["updated_date"] = match_updated_date.group(1)

    # Limit detection
    match_limit = re.search(r'limit\s*(\d+)', query.lower())
    if match_limit:
        filters["limit"] = int(match_limit.group(1))
    
    return filters

################################################################################
# 5. Main Streamlit App
################################################################################

def main():
    # Set page configuration for a professional layout
    st.set_page_config(page_title="Consumption of Petroleum Products", layout="centered")

    st.title("📊 Monthly Consumption of Petroleum Products Chatbot")

    st.markdown("""
    Welcome! Ask me any question related to the monthly consumption of petroleum products.
    
    **Examples:**
    - "Show me the consumption of LPG in 2022."
    - "I want the monthly consumption of ATF in March 2023."
    - "How much Naphtha was consumed in May 2021?"
    - "Provide the quantity of Bitumen in 2020."
    """)

    # Text input for user query
    user_query = st.text_input("🔍 Enter your query here:", "")

    if st.button("Search"):
        if user_query.strip() == "":
            st.warning("Please enter a valid query.")
        else:
            with st.spinner("Processing your request..."):
                # 1. Classify the query to determine which API to call
                api_identifier = classify_query(user_query)
                
                if not api_identifier:
                    # Unsupported query
                    st.info("""
                        🛠️ **Assistance Needed**
                        
                        It seems your query doesn't match the available data parameters. 
                        Please ask about petroleum consumption using the following filters:
                        - **Month** (e.g., January, February)
                        - **Year** (e.g., 2022, 2023)
                        - **Product** (e.g., LPG, ATF, HSD)
                        
                        **Examples:**
                        - "Show me the consumption of LPG in 2022."
                        - "I want the monthly consumption of ATF in March 2023."
                        - "How much Naphtha was consumed in May 2021?"
                        - "Provide the quantity of Bitumen in 2020."
                    """)
                else:
                    # 2. Parse the query to extract filters based on the selected API
                    if api_identifier == "consumption_petroleum":
                        filters = parse_filters_petroleum(user_query)
                    else:
                        filters = {}
                    
                    # 3. Call the appropriate API
                    result = call_api(api_identifier, filters)
                    
                    # 4. Display the results
                    if result.get("response_data"):
                        df = pd.DataFrame(result["response_data"])
                        if not df.empty:
                            st.success("✅ Data retrieved successfully!")
                            st.dataframe(df)
                            
                            # Allow the user to download the data as CSV
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Download Data as CSV",
                                data=csv,
                                file_name="petroleum_consumption.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning(result.get("message", "No data found for the given filters."))
                    else:
                        # Display assistance message if available
                        if result.get("message"):
                            st.info(result["message"])
                        else:
                            st.warning("No data found and no assistance message provided.")

################################################################################
# 6. Run the App
################################################################################

if __name__ == "__main__":
    main()
