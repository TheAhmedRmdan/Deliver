import streamlit as st
import time
import pandas as pd
from sqlalchemy.types import TIME
import re

DB_URL = st.secrets.get("connections")["sqlalchemy"]["URL"]
SEC_DB = st.secrets.get("admin")["secrets"]["secret_db"]
ORS_API_KEY = st.secrets.get("admin")["secrets"]["ORS_API_KEY"]
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
    "area": st.column_config.SelectboxColumn("Area", options=NASR_AREAS),
    "gmap": st.column_config.LinkColumn("Maps URL"),
    "street": st.column_config.TextColumn("Street"),
    "time": st.column_config.TimeColumn("Time", format="hh:mm a"),
    "whatsapp": st.column_config.LinkColumn("Whatsapp URL"),
    "delivered": st.column_config.CheckboxColumn("Delivered? "),
    "phone": st.column_config.LinkColumn("Phone"),
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
    df.to_sql(tab_name, DB_URL, if_exists="replace", index=False, dtype={"time": TIME})
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
    coords_value = str(coords_value).strip()
    df["coords"] = df["coords"].dropna()
    matching_rows = df[df["coords"].str.strip() == coords_value]
    if not matching_rows.empty:
        return str(matching_rows.iloc[0]["customer"])
    else:
        return "No customer found for the provided coords."


def generate_wa(phone: str):
    phone = phone.replace(" ", "").strip()
    pattern = r"([\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6})|([\+]?[(]?[٠-٩]{3}[)]?[-\s\.]?[٠-٩]{3}[-\s\.]?[٠-٩]{4,6})"
    base_wa_url = "https://wa.me/"
    match = re.search(pattern, phone).group()
    if not match.startswith("0"):
        match = "0" + match
    return base_wa_url + match + "/"


def generate_google_maps_directions_url(coordinates, start_from_device_location=True):
    """A function to get the google maps dir url from raw coords for the non-optimized version.
    Will be updated when the optimization API is implemented"""

    base_url = r"https://www.google.com/maps/dir/my%20location/"
    if not start_from_device_location:
        base_url = r"https://www.google.com/maps/dir/"
    url_parts = []
    for coord in coordinates:
        url_parts.append(f"{coord[0]},{coord[1]}")
    url = base_url + "/".join(url_parts)
    return url


## Possible alternative list literal eval
# coords = df["coords"].dropna().apply(lambda x: x.strip("[]").replace("'","").split(", ")).tolist()
