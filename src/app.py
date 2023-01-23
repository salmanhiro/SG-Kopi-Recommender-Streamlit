import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import pandas as pd
import numpy as np

def calculate_lat_lon_distance(lat1, lon1, lat2, lon2):
    R = 6373.0
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    return distance


def main():

    st.title("SG Kopi Recommendations")
    st.subheader("We recommend you to try these Kopi places near you!")
    st.text("Click the button below to get your location")

    loc_button = Button(label="Get Location")
    loc_button.js_on_event("button_click", CustomJS(code="""
        navigator.geolocation.getCurrentPosition(
            (loc) => {
                document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
            }
        )
        """))
    result = streamlit_bokeh_events(
        loc_button,
        events="GET_LOCATION",
        key="get_location",
        refresh_on_update=False,
        override_height=45,
        debounce_time=0)
    st.text("Or maybe looking for Kopi places beyond specific PA?")

    sg_pa = pd.read_csv("sg_pa_w_coord.csv")
    sg_pa = sg_pa[["Name", "lat", "lon"]]

    loc_list = [""]
    loc_list.extend(sg_pa["Name"].values)
    location = st.selectbox("Select your location", loc_list)
    
    loc = {}
    if result:
        if "GET_LOCATION" in result:
            gps_loc = result.get("GET_LOCATION")
            print("gps loc", gps_loc)
            loc = gps_loc
            

    if location:
        pa_loc = {"lat": sg_pa[sg_pa["Name"] == location]["lat"].values[0], "lon": sg_pa[sg_pa["Name"] == location]["lon"].values[0]}
        loc = pa_loc
        print("pa loc", pa_loc)
        
    df_kopi = pd.read_csv("full_sg_kopi.csv")
    df_kopi["distance_from_user"] = 0

    if loc:
        for i in range(len(df_kopi)):
            print(i)
            print(df_kopi.loc[i, "lat"])
            print(df_kopi.loc[i, "lon"])
            print(loc["lat"])
            print(loc["lon"])
            df_kopi.loc[i, "distance_from_user"] = calculate_lat_lon_distance(df_kopi.loc[i, "lat"], df_kopi.loc[i, "lon"], loc["lat"], loc["lon"])

        
        # show the top 10 kopi places sorted
        df_kopi = df_kopi.sort_values(by="distance_from_user")
        st.dataframe(df_kopi.head(10))



if __name__ == "__main__":
    main()