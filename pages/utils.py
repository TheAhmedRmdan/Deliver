import streamlit as st
import time
import pandas as pd
from sqlalchemy.types import TIME, INT
import re
import requests
import folium.plugins as plg
import folium
from math import ceil

DB_URL = st.secrets.get("connections")["sqlalchemy"]["URL"]
SEC_DB = st.secrets.get("admin")["secrets"]["secret_db"]
TOMTOM_API = st.secrets.get("admin")["secrets"]["TOMTOM_API"]
NASR_AREAS = [
    "ش نزهة",
    "عباس",
    "مكرم",
    "حى6",
    "حىى7",
    "حى8",
    "حى10",
    "منطقة9",
    "زهراء",
    "تبة",
    "4.5",
    "زمر",
    "حسن المأمون",
    "النصر",
    "محور المشير",
    "محور الشهيد",
    "الواحة",
    "جاردينيا",
    "الوفاء والامل",
    "النحاس",
    "المخيم الدائم",
    "مهدى عرفة",
    "يوسف عباس",
    "استاد القاهرة",
    "الفنجرى",
    "امتداد رمسيس",
    "مقاولون",
    "رابعة",
    "مساكن الشروق",
    "منشية ناصر",
    "دويقة",
]
COL_CONFIG = {
    "idx": st.column_config.NumberColumn("id"),
    "customer": st.column_config.TextColumn("العميل"),
    "area": st.column_config.SelectboxColumn("المنطقة", options=NASR_AREAS),
    "gmap": st.column_config.LinkColumn("Maps URL"),
    "street": st.column_config.TextColumn("Street"),
    "time": st.column_config.TimeColumn("الوقت", format="hh:mm a"),
    "whatsapp": st.column_config.LinkColumn("Whatsapp URL"),
    "delivered": st.column_config.CheckboxColumn("Delivered? "),
    "phone": st.column_config.LinkColumn("الهاتف"),
    "building": st.column_config.NumberColumn("عمارة"),
    "floor": st.column_config.NumberColumn("دور"),
    "apartment": st.column_config.NumberColumn("شقة"),
}


def logout():
    st.session_state["authenticated"] = False
    st.session_state.pop("df", None)
    st.cache_resource.clear()
    st.cache_data.clear()
    with st.spinner("Logging out"):
        time.sleep(2)
    st.switch_page("Login.py")


def show_logout(button_key):
    with st.sidebar:
        st.write("Welcome", st.session_state["username"])
        if st.button("Logout", key=button_key):
            logout()


def get_data(table_name):
    query = f"SELECT * FROM {table_name}"
    postgres_df = pd.read_sql(query, DB_URL)
    return postgres_df


def commit_to_db(df: pd.DataFrame, tab_name):
    df.to_sql(
        tab_name,
        DB_URL,
        if_exists="replace",
        index=False,
        dtype={
            "time": TIME,
            "idx": INT,
            "building": INT,
            "floor": INT,
            "apartment": INT,
        },
    )
    st.success("Pushed to database sucessfully", icon="✅")


def process_table(table_name):
    if table_name in SEC_DB:
        logout()
    if "df" not in st.session_state:
        st.session_state.df = None
    if st.button("Fetch Data"):
        loading_text = st.text("Fetching data...")
        st.session_state.df = get_data(table_name)
        loading_text.empty()


def get_customer_by_coords(coords_value, df):
    coords_value = str(coords_value).replace(" ", "").strip()
    df["coords"] = df["coords"].dropna()
    matching_rows = df[df["coords"].str.replace(" ", "").str.strip() == coords_value]
    if not matching_rows.empty:
        name = str(matching_rows.iloc[0]["customer"])
        bfa = (
            matching_rows[["building", "floor", "apartment"]]
            .dropna(axis=1)
            .astype(int)
            .squeeze()
        )
        building = bfa.get("building", "X")
        floor = bfa.get("floor", "X")
        apt = bfa.get("apartment", "X")
        output = f"""{name} ع:{building} د:{floor} ش:{apt}"""
        return output
    else:
        return "No customer found for the provided coords."


def generate_wa(phone: str):
    phone = phone.replace(" ", "").strip()
    pattern = r"([\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6})|([\+]?[(]?[٠-٩]{3}[)]?[-\s\.]?[٠-٩]{3}[-\s\.]?[٠-٩]{4,6})"
    base_wa_url = "https://wa.me/"
    match = re.search(pattern, phone).group()
    if not match.startswith(("0", "+2", "20")):
        match = "0" + match
    return base_wa_url + match + "/"


def convert_coords_to_api_format(old_coords: list):
    tomtom_format = []
    for coord in old_coords:
        tomtom_format.append(
            {"point": {"latitude": float(coord[0]), "longitude": float(coord[1])}}
        )
    # Append the remaining coordinates if any
    return tomtom_format


def split_iterable(coords_list, max=12):
    # Calculate the number of sublists needed
    num_sublists = ceil(len(coords_list) / max)
    # Generate the sublists
    return [coords_list[i * max : (i + 1) * max] for i in range(num_sublists)]


def get_optimized_coords(original_coords: list):
    base_url = f"https://api.tomtom.com/routing/waypointoptimization/1?key={TOMTOM_API}"
    OPTIONS = {
        "traffic": "historical",
        "waypointConstraints": {
            "originIndex": -1,
            "destinationIndex": -1,
        },
    }

    tomtom_format = convert_coords_to_api_format(original_coords)
    chunks = split_iterable(tomtom_format)
    optimized_coords_per_chunk = []
    cumulative_index = 0  # Initialize a variable to keep track of the cumulative index

    for chunk in chunks:
        json_params = {"waypoints": chunk, "options": OPTIONS}
        response = requests.post(base_url, json=json_params)
        if response.status_code == 200:
            optimizedOrder_indexes = response.json()["optimizedOrder"]

            # Adjust indexes based on the cumulative index
            adjusted_indexes = [
                (index + cumulative_index) for index in optimizedOrder_indexes
            ]

            optimized_coords_chunk = [
                original_coords[index] for index in adjusted_indexes
            ]
            optimized_coords_per_chunk.append(optimized_coords_chunk)

            cumulative_index += len(chunk)  # Update the cumulative index
        else:
            raise requests.HTTPError(
                f"API ERROR, RESPONSE CODE: {response.status_code}"
            )
        time.sleep(5)

    return optimized_coords_per_chunk


def generate_gmaps_directions_url(coordinates, start_from_device_location=True):
    """Generates a Google Maps Directions URL based on given coordinates"""
    base_url = r"https://www.google.com/maps/dir/my%20location/"
    if not start_from_device_location:
        base_url = r"https://www.google.com/maps/dir/"
    url_parts = []
    for coord in coordinates:
        url_parts.append(f"{coord[0]},{coord[1]}")
    url = base_url + "/".join(url_parts)
    return url


def add_markers_to_map(fmap, coordss, df):
    for i, loc in enumerate(coordss, start=1):
        float_loc = [float(lat) for lat in loc]
        popup = get_customer_by_coords(loc, df)
        folium.Marker(
            location=loc,
            icon=plg.BeautifyIcon(
                icon="font-awesome",
                icon_shape="marker",
                border_color="#0080FF",
                inner_icon_style="font-size:14px;padding-top:-10px",
                number=i,
            ),
            popup=popup,
        ).add_to(fmap)


# folium.Icon(prefix="fa", icon=f"{i}")
## Possible alternative list literal eval
# coords = df["coords"].dropna().apply(lambda x: x.strip("[]").replace("'","").split(", ")).tolist()


# TODO Make the starting point current device location
