import streamlit as st
import folium
import streamlit_folium as sf
from pages.utils import *
import datetime
import io


def main():
    user_table_name = st.text_input("Enter table name: ")
    process_table(user_table_name.lower())
    if st.session_state.df is not None:
        # Table
        st.subheader("Orders Table: ")
        df: pd.DataFrame = st.session_state.df
        cleaned_df = wrangle_df(df)
        shown_df = cleaned_df.drop(columns=["coords"])
        st.dataframe(shown_df, hide_index=True, column_config=COL_CONFIG)
        st.divider()

        # Map & coords processing
        st.subheader("Orders Map: ")
        coords = cleaned_df["coords"].to_list()
        optimized_coords = ors_optimize(coords)
        str_coords = convert_float_coords_to_str(optimized_coords)
        splitted_coords_lists = split_iterable(str_coords, max=15)
        fmap = folium.Map(location=coords[0], tiles="OpenStreetMap", zoom_start=13)

        # Markers
        add_markers_to_map(fmap, str_coords, df)
        sf.folium_static(fmap)
        today = datetime.datetime.now()
        filename = (
            st.session_state["username"] + "-" + today.strftime("%d-%m-%Y") + ".html"
        )
        in_memory_fp = io.BytesIO()
        fmap.save(in_memory_fp, close_file=False)
        in_memory_fp.seek(0)  # Move to the beginning of the file

        # Offer the in-memory file for download
        st.download_button(
            label="Download HTML File",
            data=in_memory_fp,
            file_name=filename,
            mime="text/html",
        )
        # Google Maps Directions
        st.divider()
        st.subheader("Google Maps Directions: ")
        for route in splitted_coords_lists:
            st.write(generate_gmaps_directions_url(route, True))


if __name__ == "__main__":
    main()
