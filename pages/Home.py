import streamlit as st
import time


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


def main():
    show_logout(button_key="Home_Logout")


if __name__ == "__main__":
    main()
