import streamlit as st
import folium
import streamlit_folium as sf
from pages.utils import *
import streamlit_js_eval as js


def main():
    show_logout(button_key="Home_Logout")
    user_table_name = st.text_input("Enter table name: ")
    process_table(user_table_name)
    if st.session_state.df is not None:
        # Table
        st.subheader("Orders Table: ")
        df: pd.DataFrame = st.session_state.df
        shown_df = df[["idx", "customer", "phone", "whatsapp", "time", "area", "gmap"]]
        shown_df["whatsapp"] = (
            shown_df["phone"]
            .dropna()
            .str.replace(" ", "")
            .str.strip()
            .apply(generate_wa)
        )
        shown_df["phone"] = (
            "tel:" + df["phone"].dropna().str.replace(" ", "").str.strip()
        )
        st.dataframe(shown_df, hide_index=True, column_config=COL_CONFIG)
        st.divider()

        # Map & coords processing
        st.subheader("Orders Map: ")
        coords = df["coords"].dropna().apply(lambda x: eval(x)).tolist()
        optimized_coords = ors_optimize(coords)
        str_coords = convert_float_coords_to_str(optimized_coords)
        splitted_coords_lists = split_iterable(str_coords, max=15)
        fmap = folium.Map(location=coords[0], tiles="cartodbvoyager", zoom_start=13)

        # Markers
        add_markers_to_map(fmap, str_coords, df)
        sf.folium_static(fmap)

        # Google Maps Directions
        st.divider()
        st.subheader("Google Maps Directions: ")
        for route in splitted_coords_lists:
            st.write(generate_gmaps_directions_url(route, False))


if __name__ == "__main__":
    main()
