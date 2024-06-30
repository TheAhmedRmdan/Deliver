import streamlit as st
import folium
import streamlit_folium as sf
from pages.utils import *
from itertools import chain


def main():
    show_logout(button_key="Home_Logout")
    user_table_name = st.text_input("Enter table name: ")
    process_table(user_table_name)
    if st.session_state.df is not None:
        # Table
        st.subheader("Orders Table: ")
        df: pd.DataFrame = st.session_state.df
        shown_df = df[["idx", "customer", "phone", "whatsapp", "time", "area", "gmap"]]
        shown_df["whatsapp"] = df["phone"].dropna().apply(generate_wa)
        shown_df["phone"] = add_tel_prefix(shown_df["phone"])
        st.dataframe(shown_df, hide_index=True, column_config=COL_CONFIG)
        st.divider()

        # Map
        st.subheader("Orders Map: ")
        coords = df["coords"].dropna().apply(lambda x: eval(x)).tolist()
        optimized_coords = get_optimized_coords(coords)
        flattened_optimized_coords = list(chain.from_iterable(optimized_coords))
        fmap = folium.Map(location=coords[0], tiles="cartodbvoyager", zoom_start=13)

        # Markers
        for i, loc in enumerate(flattened_optimized_coords, start=1):
            popup = get_customer_by_coords(loc, df)
            folium.Marker(
                loc, icon=folium.Icon(prefix="fa", icon=f"{i}"), popup=popup
            ).add_to(fmap)
        sf.folium_static(fmap)

        # Google Maps Directions
        st.divider()
        st.subheader("Google Maps Directions: ")
        for route in optimized_coords:
            st.write(generate_gmaps_directions_url(route))


if __name__ == "__main__":
    main()
