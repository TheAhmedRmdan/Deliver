import streamlit as st
import psycopg2 as ps
from st_login_form import login_form
import time

client = login_form(allow_guest=False, allow_create=False)
if st.session_state["authenticated"]:
    with st.spinner(f"Welcome {st.session_state['username']}"):
        time.sleep(2)
    if st.session_state["username"] == "entry":
        st.switch_page("pages/Entry.py")
    st.switch_page("pages/Home.py")
else:
    st.error("Not authenticated")

