import streamlit as st
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
