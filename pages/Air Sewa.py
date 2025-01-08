import streamlit as st
import requests
import re
import io
import pandas as pd

################################################################################
# 1. Define API Information
################################################################################

API_INFO = {
    "aviation_grievance": {
        "name": "Aviation Grievance - as on date",
        "endpoint": "https://api.data.gov.in/resource/7be93611-4e76-4077-8d00-6232d01367cf",
        "filters": [],  # Define specific filters if available
        "columns": [
            "category", "subcategory", "type", "totalReceived",
            "activeGrievancesWithoutEscalation", "activeGrievancesWithEscalation",
            "closedGrievancesWithoutEscalation", "closedGrievancesWithEscalation",
            "successfulTransferIn", "successfulTransferOut",
            "grievancesWithoutRatings", "grievancesWithRatings",
            "grievancesWithVeryGoodRating", "grievanceswithgoodrating",
            "grievancesWithOKRating", "grievancesWithBadRating",
            "grievancesWithVeryBadRating", "twitterGrievances",
            "facebookGrievances", "grievancesAdditionalInfoProvided",
            "grievancesAdditionalInfoNotProvided", "grievancesWithoutFeedback",
            "grievancesWithFeedback", "grievancesWithFeedbackIssueNotResolved",
            "grievancesWithFeedbackIssueResolved"
        ]
    },
    "flight_schedule": {
        "name": "Flight Schedule",
        "endpoint": "https://api.data.gov.in/resource/b71db183-2d15-4f61-9cee-7de3c83561a1",
        "filters": [
            "airline", "flightNumber", "origin", "destination",
            "daysOfWeek", "scheduledDepartureTime", "scheduledArrivalTime",
            "timezone", "validFrom", "validTo", "last_updated"
        ],
        "columns": [
            "airline", "flightNumber", "origin", "destination",
            "daysOfWeek", "scheduledDepartureTime", "scheduledArrivalTime",
            "timezone", "validFrom", "validTo", "lastUpdated"
        ]
    },
    "aviation_faqs": {
        "name": "AirSewa - Aviation Frequently Asked Questions (FAQs)",
        "endpoint": "https://api.data.gov.in/resource/bc015fd1-a544-43b1-b4a2-729475c4580c",
        "filters": [
            "category", "faqQuestion", "faqAnswer",
            "faqQuestionHindi", "faqAnswerHindi", "last_updated"
        ],
        "columns": [
            "category", "faqQuestion", "faqAnswer",
            "faqQuestionHindi", "faqAnswerHindi", "lastUpdated"
        ]
    },
    "airport_services": {
        "name": "AirSewa - Airport Services Data",
        "endpoint": "https://api.data.gov.in/resource/93710e81-db2b-4f95-9223-89156dfd8bc9",
        "filters": [
            "airport", "categoryenglish", "categoryHindi",
            "titleEnglish", "titleHindi", "descriptionEnglish",
            "descriptionHindi", "email", "phone", "website", "last_updated"
        ],
        "columns": [
            "airport", "categoryenglish", "categoryHindi",
            "titleEnglish", "titleHindi", "descriptionEnglish",
            "descriptionHindi", "email", "phone", "website", "last_updated"
        ]
    }
}


################################################################################
# 2. API Call Function
################################################################################

def call_api(api_identifier, filters, format_type="csv"):
    # Map API identifiers to their respective API keys from secrets
    api_key_mapping = {
        "aviation_grievance": st.secrets["AVIATION_GRI_API_KEY"],
        "flight_schedule": st.secrets["FLIGHT_SCHEDULE_API_KEY"],
        "aviation_faqs": st.secrets["AV_FAQ_API_KEY"],
        "airport_services": st.secrets["AIRPORT_SERVICES_API_KEY"]
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
        "limit": filters.get("limit", 10)
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
    Determine which API to call based on keywords in the user's query.
    Returns the API identifier or None if no match is found.
    """
    query_lower = query.lower()

    # Define keywords for each API
    keywords = {
        "aviation_grievance": ["grievance", "complaint", "issue"],
        "flight_schedule": ["flight schedule", "flight status", "flight number", "departure", "arrival"],
        "aviation_faqs": ["faq", "frequently asked questions", "question", "answer"],
        "airport_services": ["airport services", "services", "facility", "services data"]
    }

    for api_id, kws in keywords.items():
        for kw in kws:
            if kw in query_lower:
                return api_id

    return None


################################################################################
# 4. Filter Parsing Functions for Each API
################################################################################

def parse_filters_aviation_grievance(query):
    """
    Parse filters specific to the Aviation Grievance API.
    Currently, no specific filters are defined beyond default pagination.
    """
    filters = {
        "offset": 0,
        "limit": 10,
        "format": "csv"  # Always CSV for consistency
    }

    # Example: User might specify limit
    match_limit = re.search(r'limit\s*(\d+)', query.lower())
    if match_limit:
        filters["limit"] = int(match_limit.group(1))

    # Add more parsing logic as per available filters if needed

    return filters


def parse_filters_flight_schedule(query):
    """
    Parse filters specific to the Flight Schedule API.
    """
    filters = {
        "offset": 0,
        "limit": 10,
        "format": "csv"
    }

    # Airline
    airlines = ["IndiGo", "GoAir", "Jet Airways", "Air India", "Etihad Airways", "Vistara", "British Airways",
                "Thai Airways"]
    for airline in airlines:
        if airline.lower() in query.lower():
            filters["airline"] = airline
            break

    # Flight Number
    match_flight = re.search(r'flight\s*number\s*(\w+)', query.lower())
    if match_flight:
        filters["flightNumber"] = match_flight.group(1).upper()

    # Origin and Destination
    match_origin = re.search(r'from\s+([A-Za-z\s]+)', query.lower())
    if match_origin:
        filters["origin"] = match_origin.group(1).strip().title()

    match_destination = re.search(r'to\s+([A-Za-z\s]+)', query.lower())
    if match_destination:
        filters["destination"] = match_destination.group(1).strip().title()

    # Days of Week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    found_days = [day for day in days if day.lower() in query.lower()]
    if found_days:
        filters["daysOfWeek"] = ",".join(found_days)

    # Scheduled Departure and Arrival Times
    match_dep = re.search(r'departure\s+time\s*[:\-]?\s*(\d{1,2}:\d{2})', query.lower())
    if match_dep:
        filters["scheduledDepartureTime"] = match_dep.group(1)

    match_arr = re.search(r'arrival\s+time\s*[:\-]?\s*(\d{1,2}:\d{2})', query.lower())
    if match_arr:
        filters["scheduledArrivalTime"] = match_arr.group(1)

    # Timezone
    match_timezone = re.search(r'timezone\s*[:\-]?\s*([\w\s/]+)', query.lower())
    if match_timezone:
        filters["timezone"] = match_timezone.group(1).strip().title()

    # Valid From and To
    match_valid_from = re.search(r'valid\s*from\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})', query.lower())
    if match_valid_from:
        filters["validFrom"] = match_valid_from.group(1)

    match_valid_to = re.search(r'valid\s*to\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})', query.lower())
    if match_valid_to:
        filters["validTo"] = match_valid_to.group(1)

    # Last Updated
    match_last_updated = re.search(r'last\s*updated\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})', query.lower())
    if match_last_updated:
        filters["last_updated"] = match_last_updated.group(1)

    # Limit
    match_limit = re.search(r'limit\s*(\d+)', query.lower())
    if match_limit:
        filters["limit"] = int(match_limit.group(1))

    return filters


def parse_filters_aviation_faqs(query):
    """
    Parse filters specific to the Aviation FAQs API.
    """
    filters = {
        "offset": 0,
        "limit": 10,
        "format": "csv"
    }

    # Category
    categories = ["Passenger", "Cargo", "Security", "Facilities"]
    for category in categories:
        if category.lower() in query.lower():
            filters["category"] = category
            break

    # FAQ Question
    match_question = re.search(r'question\s*[:\-]?\s*(.+)', query, re.IGNORECASE)
    if match_question:
        filters["faqQuestion"] = match_question.group(1).strip()

    # FAQ Answer
    match_answer = re.search(r'answer\s*[:\-]?\s*(.+)', query, re.IGNORECASE)
    if match_answer:
        filters["faqAnswer"] = match_answer.group(1).strip()

    # Hindi Fields (optional)
    match_question_hindi = re.search(r'question\s+hindi\s*[:\-]?\s*(.+)', query, re.IGNORECASE)
    if match_question_hindi:
        filters["faqQuestionHindi"] = match_question_hindi.group(1).strip()

    match_answer_hindi = re.search(r'answer\s+hindi\s*[:\-]?\s*(.+)', query, re.IGNORECASE)
    if match_answer_hindi:
        filters["faqAnswerHindi"] = match_answer_hindi.group(1).strip()

    # Last Updated
    match_last_updated = re.search(r'last\s*updated\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})', query.lower())
    if match_last_updated:
        filters["last_updated"] = match_last_updated.group(1)

    # Limit
    match_limit = re.search(r'limit\s*(\d+)', query.lower())
    if match_limit:
        filters["limit"] = int(match_limit.group(1))

    return filters


def parse_filters_airport_services(query):
    """
    Parse filters specific to the Airport Services Data API.
    """
    filters = {
        "offset": 0,
        "limit": 10,
        "format": "csv"
    }

    # Airport
    airports = ["Chennai", "Mumbai", "Bengaluru", "Indore", "Delhi", "Hyderabad"]
    for airport in airports:
        if airport.lower() in query.lower():
            filters["airport"] = airport
            break

    # Category English and Hindi
    categories_eng = ["Parking and Transportation", "Special Assistance Services"]
    for cat in categories_eng:
        if cat.lower() in query.lower():
            filters["categoryenglish"] = cat
            break

    categories_hin = ["पार्किंग और परिवहन", "विशेष सहायता सेवाएँ"]
    for cat in categories_hin:
        if cat.lower() in query.lower():
            filters["categoryHindi"] = cat
            break

    # Title English and Hindi
    match_title_eng = re.search(r'title\s*english\s*[:\-]?\s*(.+)', query, re.IGNORECASE)
    if match_title_eng:
        filters["titleEnglish"] = match_title_eng.group(1).strip()

    match_title_hin = re.search(r'title\s*hindi\s*[:\-]?\s*(.+)', query, re.IGNORECASE)
    if match_title_hin:
        filters["titleHindi"] = match_title_hin.group(1).strip()

    # Description English and Hindi
    match_desc_eng = re.search(r'description\s*english\s*[:\-]?\s*(.+)', query, re.IGNORECASE)
    if match_desc_eng:
        filters["descriptionEnglish"] = match_desc_eng.group(1).strip()

    match_desc_hin = re.search(r'description\s*hindi\s*[:\-]?\s*(.+)', query, re.IGNORECASE)
    if match_desc_hin:
        filters["descriptionHindi"] = match_desc_hin.group(1).strip()

    # Email, Phone, Website
    match_email = re.search(r'email\s*[:\-]?\s*([\w\.-]+@[\w\.-]+)', query, re.IGNORECASE)
    if match_email:
        filters["email"] = match_email.group(1)

    match_phone = re.search(r'phone\s*[:\-]?\s*(\d{10,15})', query, re.IGNORECASE)
    if match_phone:
        filters["phone"] = match_phone.group(1)

    match_website = re.search(r'website\s*[:\-]?\s*(https?://\S+)', query, re.IGNORECASE)
    if match_website:
        filters["website"] = match_website.group(1)

    # Last Updated
    match_last_updated = re.search(r'last\s*updated\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})', query.lower())
    if match_last_updated:
        filters["last_updated"] = match_last_updated.group(1)

    # Limit
    match_limit = re.search(r'limit\s*(\d+)', query.lower())
    if match_limit:
        filters["limit"] = int(match_limit.group(1))

    return filters


################################################################################
# 5. Main Streamlit App
################################################################################

def main():
    # Set page configuration for a professional layout
    st.set_page_config(page_title="Air Sewa Chatbot", layout="wide")

    st.title("✈️ Air Sewa Chatbot")

    st.markdown("""
    Welcome! Ask me any question related to Air Sewa services, aviation grievances, flight schedules, or frequently asked questions.

    **Examples:**
    - "Show me the aviation grievances for Ethiopian Airlines in 2024."
    - "What is the flight schedule for IndiGo flight 451 from Bengaluru to Lucknow?"
    - "I have a question about Jet Airways baggage services."
    - "Where are the pharmacy services at Mumbai Airport?"

    If your query isn't related to the available data, I'll assist you with a workaround.
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
                        Please ask about Air Sewa using the following categories:
                        - **Aviation Grievances**
                        - **Flight Schedule**
                        - **Frequently Asked Questions (FAQs)**
                        - **Airport Services**

                        **Examples:**
                        - "Show me the aviation grievances for Ethiopian Airlines in 2024."
                        - "What is the flight schedule for IndiGo flight 451 from Bengaluru to Lucknow?"
                        - "I have a question about Jet Airways baggage services."
                        - "Where are the pharmacy services at Mumbai Airport?"
                    """)
                else:
                    # 2. Parse the query to extract filters based on the selected API
                    if api_identifier == "aviation_grievance":
                        filters = parse_filters_aviation_grievance(user_query)
                    elif api_identifier == "flight_schedule":
                        filters = parse_filters_flight_schedule(user_query)
                    elif api_identifier == "aviation_faqs":
                        filters = parse_filters_aviation_faqs(user_query)
                    elif api_identifier == "airport_services":
                        filters = parse_filters_airport_services(user_query)
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
                                file_name="airsewa_data.csv",
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
