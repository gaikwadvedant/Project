from pathlib import Path
import folium
from geopy.geocoders import Nominatim
from jinja2 import Template 
import numpy as np
import ollama
import streamlit as st
from streamlit_folium import st_folium

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"

st.set_page_config(
    page_title="BhumiPulse  | House Price Prediction ",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #0b132b;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    .header-box {
        background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
        padding: 24px;
        border-radius: 14px;
        border: 1px solid #3a506b;
        margin-bottom: 20px;
    }
    .header-title {
        color: #6fffe9;
        font-size: 30px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #5bc0be;
        font-size: 14px;
        margin-top: 4px;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #5bc0be 0%, #3a506b 100%);
        color: #0b132b;
        font-weight: 700;
        border-radius: 10px;
        border: none;
        padding: 12px;
        width: 100%;
    }
    .dynamic-box {
        background-color: #162238;
        border-left: 4px solid #6fffe9;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: #162238;
        border: 1px solid #3a506b;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-label {
        color: #5bc0be;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        color: #ffffff;
        font-size: 24px;
        font-weight: 700;
        margin-top: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

if "selected_prop_type" not in st.session_state:
    st.session_state["selected_prop_type"] = "Apartment"
if "has_calculated" not in st.session_state:
    st.session_state["has_calculated"] = False
if "calc_results" not in st.session_state:
    st.session_state["calc_results"] = {}
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

geolocator = Nominatim(user_agent="bhumipulse_ai_engine")

st.markdown(
    """
    <div class="header-box">
        <div class="header-title">⚡ BhumiPulse</div>
        <div class="header-subtitle">Next-Gen Spatial house price Valuation & Financial Intelligence Platform</div>
    </div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("⚙️ Engine Controls")
    selected_ai_model = st.selectbox(
        "Local LLM Engine", options=["llama3.2:3b", "llama3:latest"], index=0
    )
    enable_ai = st.toggle("Generate AI Strategic Report", value=True)
    st.divider()
    st.markdown("### 📊 Market Benchmarks")
    interest_rate = st.slider(
        "Home Loan Interest Rate (%)", 7.0, 12.0, 8.5, 0.1
    )
    tenure_years = st.slider("Loan Tenure (Years)", 5, 30, 20, 5)

col_search, col_info = st.columns([2, 1])

with col_search:
    location_query = st.text_input(
        "🔍 Target City, Locality, or Village (All-India):",
        value="Kalyan West, Maharashtra",
        placeholder="Type any place name in India...",
    )

location_info = None
if location_query:
    try:
        query_str = (
            f"{location_query}, India"
            if "India" not in location_query
            else location_query
        )
        location_info = geolocator.geocode(query_str)
    except Exception as e:
        st.error(f"Geocoding service error: {e}")

if location_info:
    lat, lon = location_info.latitude, location_info.longitude
    formatted_address = location_info.address
    with col_info:
        st.info(f"**GPS Coordinates:** `{lat:.4f}, {lon:.4f}`")
else:
    lat, lon = 19.2437, 73.1355
    formatted_address = location_query

st.subheader("📋 Select Property Category")

def on_prop_type_change():
    st.session_state["selected_prop_type"] = st.session_state["prop_type_radio"]

prop_type = st.radio(
    "Choose Property Type:",
    ["Apartment", "Bungalow / Villa", "Independent House", "Builder Floor"],
    key="prop_type_radio",
    on_change=on_prop_type_change,
    horizontal=True,
)

f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    bhk = st.selectbox("BHK Configuration", [1, 2, 3, 4, 5, 6, 8], index=2)
    furnishing = st.selectbox(
        "Furnishing Status",
        ["Unfurnished", "Semi-Furnished", "Fully Furnished"],
        index=1,
    )

with f_col2:
    size_sqft = st.number_input(
        "Built-up Area (Sq. Ft.)",
        min_value=250,
        max_value=35000,
        value=2400 if "Villa" in st.session_state["selected_prop_type"] or "House" in st.session_state["selected_prop_type"] else 950,
        step=50,
    )

with f_col3:
    dist_rail = st.slider("Railway Distance (KM)", 0.0, 10.0, 2.0, 0.1)

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state["selected_prop_type"] in ["Bungalow / Villa", "Independent House"]:
    st.markdown(
        """
        <div class="dynamic-box">
            <h4 style="color: #6fffe9; margin-top: 0;">🏡 Villa / Independent House Specifications</h4>
            Configure structure height, plot details, and private parking capacity.
        </div>
        """,
        unsafe_allow_html=True,
    )
    v_col1, v_col2, v_col3 = st.columns(3)
    with v_col1:
        floors = st.selectbox(
            "Structure Height (Floors)",
            ["G (Single Floor)", "G+1 (2 Floors)", "G+2 (3 Floors)", "G+3 (4 Floors)"],
            index=1,
            key="villa_floors",
        )
    with v_col2:
        parking_spaces = st.selectbox(
            "Private Parking / Garage Capacity",
            ["1 Private Car Park", "2 Private Car Parks", "3+ Private Slots / Covered Garage"],
            index=1,
            key="villa_parking",
        )
    with v_col3:
        plot_size = st.number_input(
            "Plot Area (Sq. Ft.)",
            min_value=500,
            max_value=50000,
            value=3000,
            step=100,
            key="villa_plot",
        )
else:
    st.markdown(
        """
        <div class="dynamic-box">
            <h4 style="color: #6fffe9; margin-top: 0;">🏢 Apartment / Builder Floor Specifications</h4>
            Configure building floor position and assigned parking slots.
        </div>
        """,
        unsafe_allow_html=True,
    )
    a_col1, a_col2 = st.columns(2)
    with a_col1:
        floors = st.selectbox(
            "Floor Level Position",
            ["Ground / Lower Floor", "Mid Floor (Floors 2-10)", "High Floor / Penthouse (Floors 11+)"],
            index=1,
            key="apt_floors",
        )
    with a_col2:
        parking_spaces = st.selectbox(
            "Assigned Parking Slots",
            ["No Dedicated Slot", "1 Covered Slot", "2 Covered Slots"],
            index=1,
            key="apt_parking",
        )
    plot_size = size_sqft

submit_calc = st.button("Run Analytics & Generate Valuation")

if submit_calc:
    active_type = st.session_state["selected_prop_type"]
    transit_score = round(max(0, 100 - (dist_rail * 10)), 1)
    dist_from_mumbai = np.sqrt((lat - 19.0760) ** 2 + (lon - 72.8777) ** 2)

    if dist_from_mumbai < 0.2:
        base_rate = 38000
    elif dist_from_mumbai < 0.8:
        base_rate = 9200
    else:
        base_rate = 6200

    if active_type == "Bungalow / Villa":
        type_mult = 1.45
    elif active_type == "Independent House":
        type_mult = 1.30
    elif active_type == "Builder Floor":
        type_mult = 1.10
    else:
        type_mult = 1.00

    furnish_mult = (
        1.12
        if furnishing == "Fully Furnished"
        else (1.05 if furnishing == "Semi-Furnished" else 1.0)
    )

    if "3+" in parking_spaces or "2 Private" in parking_spaces:
        parking_mult = 1.10
    elif "2 Covered" in parking_spaces or "1 Private" in parking_spaces:
        parking_mult = 1.05
    else:
        parking_mult = 1.00

    if active_type in ["Bungalow / Villa", "Independent House"]:
        if "G+2" in floors:
            floor_mult = 1.05
        elif "G+3" in floors:
            floor_mult = 1.08
        else:
            floor_mult = 1.00
    else:
        if "High Floor" in floors:
            floor_mult = 1.04
        else:
            floor_mult = 1.00

    total_multiplier = type_mult * furnish_mult * parking_mult * floor_mult
    sqft_price = int(base_rate * total_multiplier)
    estimated_val = (size_sqft * sqft_price) / 100000

    min_price = round(estimated_val * 0.88, 2)
    max_price = round(estimated_val * 1.12, 2)
    avg_price = round((min_price + max_price) / 2, 2)

    st.session_state["has_calculated"] = True
    st.session_state["calc_results"] = {
        "min_price": min_price,
        "max_price": max_price,
        "avg_price": avg_price,
        "sqft_price": sqft_price,
        "transit_score": transit_score,
        "lat": lat,
        "lon": lon,
        "dist_rail": dist_rail,
        "bhk": bhk,
        "prop_type": active_type,
        "size_sqft": size_sqft,
        "plot_size": plot_size,
        "furnishing": furnishing,
        "floors": floors,
        "parking_spaces": parking_spaces,
        "formatted_address": formatted_address,
        "location_query": location_query,
    }

if st.session_state["has_calculated"]:
    res = st.session_state["calc_results"]

    st.markdown("<br>", unsafe_allow_html=True)

    if TEMPLATE_PATH.exists():
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = Template(f.read())

        rendered_html = template.render(
            avg_price=res["avg_price"],
            min_price=res["min_price"],
            max_price=res["max_price"],
            sqft_price=res["sqft_price"],
            transit_score=res["transit_score"],
            formatted_address=res["formatted_address"],
        )

        st.html(rendered_html)
    else:
        st.error(f"Template file not found at: `{TEMPLATE_PATH}`. Make sure `templates/index.html` exists in your project folder.")

    tab_map, tab_emi, tab_ai, tab_chat = st.tabs(
        [
            "🗺️ Interactive GIS Map",
            "💳 Interactive EMI & Loan Calculator",
            "🤖 AI Market Intelligence",
            "💬 Project & Valuation Assistant",
        ]
    )

    with tab_map:
        map_obj = folium.Map(
            location=[res["lat"], res["lon"]],
            zoom_start=13,
            tiles="OpenStreetMap",
        )

        folium.Marker(
            location=[res["lat"], res["lon"]],
            popup=f"<b>Property Target</b><br>{res['location_query']}",
            tooltip="Property Location",
            icon=folium.Icon(color="red", icon="home", prefix="fa"),
        ).add_to(map_obj)

        station_lat = res["lat"] - (res["dist_rail"] * 0.009)
        station_lon = res["lon"] - (res["dist_rail"] * 0.009)

        folium.Marker(
            location=[station_lat, station_lon],
            popup="<b>Transit Hub</b>",
            tooltip="Transit Station",
            icon=folium.Icon(color="blue", icon="train", prefix="fa"),
        ).add_to(map_obj)

        folium.PolyLine(
            locations=[[res["lat"], res["lon"]], [station_lat, station_lon]],
            color="#5bc0be",
            weight=3,
            opacity=0.8,
            tooltip=f"{res['dist_rail']} KM Proximity",
        ).add_to(map_obj)

        st_folium(
            map_obj,
            width=1200,
            height=450,
            key=f"map_{res['lat']}_{res['lon']}",
        )

    with tab_emi:
        st.subheader("💳 Financial Feasibility & EMI Calculator")

        loan_col1, loan_col2 = st.columns(2)
        with loan_col1:
            down_payment_pct = st.slider("Down Payment (%)", 10, 50, 20, 5)
            total_principal = (res["avg_price"] * 100000) * (
                1 - (down_payment_pct / 100)
            )

            r = (interest_rate / 12) / 100
            n = tenure_years * 12
            monthly_emi = (
                total_principal * r * ((1 + r) ** n) / (((1 + r) ** n) - 1)
            )

        with loan_col2:
            principal_lakhs = round(total_principal / 100000, 2)
            st.markdown(
                f"""
                <div class="metric-card" style="margin-top: 10px;">
                    <div class="metric-label">Estimated Monthly EMI</div>
                    <div class="metric-value" style="color: #6fffe9; font-size: 28px;">₹ {int(monthly_emi):,} / month</div>
                    <p style="color: #5bc0be; font-size: 12px; margin-top: 8px;">
                        Principal Loan Amount: ₹ {principal_lakhs} L (₹ {int(total_principal):,}) | Down Payment: {down_payment_pct}%
                    </p>
                </div>
            """,
                unsafe_allow_html=True,
            )

    with tab_ai:
        if enable_ai:
            ai_prompt = f"""
            You are a senior real estate analyst. Provide a professional evaluation report for:
            - Address: {res['formatted_address']}
            - Property Specs: {res['bhk']} BHK {res['prop_type']}, Built-up Area: {res['size_sqft']} sq. ft., Plot Area: {res['plot_size']} sq. ft.
            - Furnishing: {res['furnishing']}
            - Structure & Parking: {res['floors']}, {res['parking_spaces']}
            - Valuation Range: ₹{res['min_price']} Lakhs - ₹{res['max_price']} Lakhs (Avg: ₹{res['avg_price']} Lakhs)
            - Proximity: Rail {res['dist_rail']} km (Transit Index: {res['transit_score']}/100)

            Structure response in 3 sections:
            1. **Valuation & Land Premium Benchmarking**: Assess how land ownership ({res['prop_type']}) and floor levels impact total market value.
            2. **Parking & Structure Impact**: Evaluate how private parking/garage capacity adds long-term value.
            3. **Investment Outlook**: Strategic advice regarding capital appreciation vs rental yield.
            Keep formatting clean and professional.
            """

            def stream_ollama():
                try:
                    response = ollama.chat(
                        model=selected_ai_model,
                        messages=[{"role": "user", "content": ai_prompt}],
                        stream=True,
                        keep_alive="2m",
                    )
                    for chunk in response:
                        yield chunk["message"]["content"]
                except Exception as e:
                    yield f"⚠️ Could not connect to local Ollama. Ensure `ollama serve` is active. Details: {e}"

            st.write_stream(stream_ollama)
        else:
            st.info(
                "Enable the 'Generate AI Strategic Report' toggle in the sidebar to stream analysis."
            )

    with tab_chat:
        st.subheader("💬 Project & Financial Assistant")
        st.caption("Ask questions about this property valuation, project specifications, location metrics, or loan finances.")

        system_instruction = f"""
        You are an AI Assistant for the BhumiPulse Real Estate Intelligence project.
        You ONLY answer questions directly related to:
        1. This real estate application project (tech stack, algorithms, UI components, how it works).
        2. The current property valuation details:
           - Location: {res['formatted_address']}
           - Property Type: {res['prop_type']} ({res['bhk']} BHK)
           - Area: {res['size_sqft']} sqft (Plot: {res['plot_size']} sqft)
           - Furnishing: {res['furnishing']} | Floors: {res['floors']} | Parking: {res['parking_spaces']}
           - Valuation Range: ₹{res['min_price']} - ₹{res['max_price']} Lakhs (Avg: ₹{res['avg_price']} L, Rate: ₹{res['sqft_price']}/sqft)
           - Transit Score: {res['transit_score']}/100 (Railway dist: {res['dist_rail']} km)
        3. Financial and EMI details (interest rate: {interest_rate}%, loan tenure: {tenure_years} years).

        STRICT RULE: If the user asks about ANY general, non-project topic (e.g., general news, coding unrelated to this app, recipes, entertainment, sports, history, weather outside project scope), DECLINE politely by stating:
        "I am strictly configured to answer questions about the BhumiPulse real estate project, current property valuation metrics, and financial calculations."
        """

        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if user_query := st.chat_input("Ask a question about this valuation, loan parameters, or project architecture..."):
            st.session_state["chat_messages"].append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            messages_payload = [{"role": "system", "content": system_instruction}]
            for msg in st.session_state["chat_messages"]:
                messages_payload.append({"role": msg["role"], "content": msg["content"]})

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                try:
                    response = ollama.chat(
                        model=selected_ai_model,
                        messages=messages_payload,
                        stream=True,
                    )
                    for chunk in response:
                        full_response += chunk["message"]["content"]
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    full_response = f"⚠️ Could not generate response. Ensure `ollama serve` is running. Details: {e}"
                    message_placeholder.markdown(full_response)

            st.session_state["chat_messages"].append({"role": "assistant", "content": full_response})