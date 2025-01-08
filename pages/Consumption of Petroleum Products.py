import streamlit as st
import requests
import re
import io
import pandas as pd


# Minimal parse logic: pick out month, year, product, etc.
def parse_query(query: str):
    filters = {
        "month": None,
        "year": None,
        "products": None,
        "quantity_000_metric_tonnes_": None,
        "updated_date": None,
        # We will force CSV so user “directly sees the csv”
        "format": "csv",
        # Default pagination
        "offset": 0,
        "limit": 15
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

    return filters


# Call the API with forced CSV output
def call_api(filters, api_key="579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"):
    url = "https://api.data.gov.in/resource/7b624b4a-1456-4945-80d0-dfb5e40ddcff"
    params = {
        "api-key": api_key,
        "format": "csv",  # Always CSV
        "offset": filters["offset"],
        "limit": filters["limit"]
    }
    if filters["month"]:
        params["filters[_month_]"] = filters["month"]
    if filters["year"]:
        params["filters[year]"] = filters["year"]
    if filters["products"]:
        params["filters[products]"] = filters["products"]
    if filters["quantity_000_metric_tonnes_"]:
        params["filters[quantity_000_metric_tonnes_]"] = filters["quantity_000_metric_tonnes_"]
    if filters["updated_date"]:
        params["filters[updated_date]"] = filters["updated_date"]

    response = requests.get(url, params=params)
    print(response.content)
    return response


def main():
    # Set page configuration for a professional layout
    st.set_page_config(page_title="Petroleum Consumption Chatbot", layout="centered")

    st.title("📊 Monthly Consumption of Petroleum Products Chatbot")

    st.markdown("""
    Welcome! Ask me any question related to the monthly consumption of petroleum products.
    """)

    # Text input for user query
    user_query = st.text_input("🔍 Enter your query here:", "")

    if st.button("Search"):
        if user_query.strip() == "":
            st.warning("Please enter a valid query.")
        else:
            with st.spinner("Processing your request..."):
                # 1. Parse the user's natural language query into filters
                filters = parse_query(user_query)

                # Check if any primary filters are set (month, year, products)
                if not any([filters["month"], filters["year"], filters["products"],
                            filters["quantity_000_metric_tonnes_"], filters["updated_date"]]):
                    # If no filters are found, provide assistance message
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
                    """)
                else:
                    # 2. Call API (always CSV)
                    response = call_api(filters)

                    if response.status_code == 200:
                        try:
                            # Parse CSV response into DataFrame
                            df = pd.read_csv(io.StringIO(response.text))

                            if df.empty:
                                st.warning("No data found for the given filters.")
                            else:
                                st.subheader("📈 Results")
                                st.dataframe(df)

                                # Allow the user to download the data as CSV
                                csv = df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="📥 Download Data as CSV",
                                    data=csv,
                                    file_name="petroleum_consumption.csv",
                                    mime="text/csv"
                                )
                        except Exception as e:
                            st.error(f"❌ Failed to parse CSV data: {e}")
                    else:
                        st.error(f"❌ Error: Unable to retrieve data (HTTP {response.status_code}).")


if __name__ == "__main__":
    main()
