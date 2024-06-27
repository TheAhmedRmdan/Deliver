import streamlit as st
import pandas as pd
from sqlalchemy.types import TIME
import time
from pages.Home import logout, show_logout


def get_data(table_name):
    query = f"SELECT * FROM {table_name}"
    postgres_df = pd.read_sql(query, DB_URL)
    return postgres_df


def commit_to_db(df: pd.DataFrame, tab_name):
    df.to_sql(tab_name, DB_URL, if_exists="replace", index=False, dtype={"time": TIME})
    st.success("Pushed to database sucessfully", icon="✅")


DB_URL = st.secrets.get("connections")["sqlalchemy"]["URL"]
SEC_DB = st.secrets.get("admin")["secrets"]["secret_db"]
NASR_AREAS = ["مكرم عبيد", "الزهراء", "العاشر", "السادس", "السابع"]
COL_CONFIG = {
    "area": st.column_config.SelectboxColumn("Area", options=NASR_AREAS),
    "gmap": st.column_config.LinkColumn("Maps URL"),
    "street": st.column_config.TextColumn("Street"),
    "time": st.column_config.TimeColumn("Time", format="hh:mm a"),
    "whatsapp": st.column_config.LinkColumn("Whatsapp URL"),
}


def main():
    show_logout(button_key="Entry_Logout")
    table_name = st.text_input("Database table name: ")
    if table_name in SEC_DB:
        logout()

    if "df" not in st.session_state:
        st.session_state.df = None

    if st.button("Fetch Data"):
        st.write("Fetching data...")
        st.session_state.df = get_data(table_name)

    if st.session_state.df is not None:
        with st.form("Edit_form"):
            edited_df = st.data_editor(
                st.session_state.df, hide_index=True, column_config=COL_CONFIG
            )
            submitted = st.form_submit_button("Submit modified data")
            if submitted:
                commit_to_db(edited_df, table_name)
                # Clear the session state after sending
                st.session_state.df = None
    else:
        st.write("No data fetched yet.")


if __name__ == "__main__":
    main()
