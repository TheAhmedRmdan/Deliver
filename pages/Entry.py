import streamlit as st
from pages.utils import *

COL_ORDER = [
    "idx",
    "customer",
    "phone",
    "time",
    "area",
    "gmap",
    "building",
    "floor",
    "apartment",
    "delivered",
]


def main():
    show_logout(button_key="Entry_Logout")
    table_name = st.text_input("Database table name: ")
    process_table(table_name)
    if st.session_state.df is not None:
        with st.form("Edit_form"):
            edited_df = st.data_editor(
                st.session_state.df,
                hide_index=True,
                column_config=COL_CONFIG,
                num_rows="dynamic",
                column_order=COL_ORDER,
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
