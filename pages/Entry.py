import streamlit as st
import pandas as pd
from sqlalchemy.types import TIME
import time


def show_logout():
    with st.sidebar:
        st.write("Welcome", st.session_state["username"])
        if st.button("Logout"):
            st.session_state["authenticated"] = False
            with st.spinner("Logging out"):
                time.sleep(2)
            st.switch_page("Login.py")


show_logout()
DSN = st.secrets.get("connections")["psycopg"]["DSN"]
DB_URL = st.secrets.get("connections")["sqlalchemy"]["URL"]

NASR_AREAS = ["مكرم عبيد", "الزهراء", "العاشر", "السادس", "السابع"]
col_config = {
    "area": st.column_config.SelectboxColumn("Area", options=NASR_AREAS),
    "gmap": st.column_config.LinkColumn("Maps URL"),
    "street": st.column_config.TextColumn("Street"),
    "time": st.column_config.TimeColumn("Time", format="hh:mm a"),
    "whatsapp": st.column_config.LinkColumn("Whatsapp URL"),
}

table_name = st.text_input("Database table name: ")
if st.button("Connect to database"):
    query = f"SELECT * FROM {table_name}"
    postgres_df = pd.read_sql(query, DB_URL)
    data = st.data_editor(postgres_df, hide_index=True, column_config=col_config)

    if st.button("Submit to database"):
        data.to_sql(
            table_name, DB_URL, if_exists="replace", index=False, dtype={"time": TIME}
        )
        st.success("Pushed to database sucessfully", icon="✅")
