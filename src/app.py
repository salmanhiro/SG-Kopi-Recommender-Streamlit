import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
import dask.dataframe as dd
import numba
import numpy as np
import time
import datetime
import pandas as pd
import plotly.graph_objects as go
from streamlit_js_eval import streamlit_js_eval

def create_link(url:str) -> str:
    return f'''<a href="{url}">Map direction 🗺️📍</a>'''

def create_link_with_name(url:str, name: str) -> str:
    return f'''<a href="{url}">{name}</a>'''

@numba.jit
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

def generate_gmaps_direction_url(src_lat, src_lon, dest_lat, dest_lon):
    url = f"https://www.google.com/maps/dir/{src_lat},{src_lon}/{dest_lat},{dest_lon}"
    return url 

def generate_gsearch_url(name, address):
    name = name.replace(" ", "-")
    address = address.replace(" ", "-")
    url = f"https://www.google.com/search?q={name}-{address}"
    return url


def main():

    st.title("SG Kopi Recommendations ☕ 🇸🇬")
    st.subheader("We recommend you to try these Kopi places near you!")

    popular_chain = st.checkbox("Include mainstream coffee chain? (e.g. Starbucks, Coffee Bean, Toast Box etc.) 🌏", value=True)
    rating_above_45 = st.checkbox("Rating above 4.5 only? ⭐️", value=False)
    open_only = st.checkbox("Currently open coffee shop only? ⏱", value=True)
    #st.text("Click the button below to get your location 📍")

    st.text("Looking for Kopi places beyond specific PA? 🚌")

    sg_pa = dd.read_csv("sg_pa_w_coord.csv").compute()
    sg_pa = sg_pa[["Name", "lat", "lon"]]

    loc_list = [""]
    loc_list.extend(sg_pa["Name"].values)
    location = st.selectbox("Select your location", loc_list)    

    
    current_time_hrs_min = time.strftime("%H:%M")

    df_kopi = dd.read_csv("full_sg_kopi.csv").compute()
    
    
    df_kopi["distance_from_user"] = 0

    if location:
        loc = {"lat": sg_pa[sg_pa["Name"] == location]["lat"].values[0], "lon": sg_pa[sg_pa["Name"] == location]["lon"].values[0]}
        if popular_chain == False:
            df_kopi = df_kopi[df_kopi["is_mainstream_chain"] == 0]
        if rating_above_45 == True:
            df_kopi = df_kopi[df_kopi["rating"] >= 4.5]
        if open_only == True:
            print("open_only",open_only)
            df_kopi['status'] = 'closed'
            current_day = datetime.datetime.now().strftime("%a").lower()
            current_time_hrs_min = time.strftime("%H:%M")
            current_time_hrs_min = datetime.datetime.strptime(current_time_hrs_min, '%H:%M')
            print('current_time_hrs_min',current_time_hrs_min)
            print(type(current_time_hrs_min))
            open_time = pd.to_datetime(df_kopi[f'{current_day}_open'], format='%Y-%m-%d %H:%M:%S')
            print('open_time',open_time)
            close_time = pd.to_datetime(df_kopi[f'{current_day}_close'], format='%Y-%m-%d %H:%M:%S')
            mask = (open_time <= current_time_hrs_min) & (current_time_hrs_min <= close_time)
            df_kopi["status"][mask] = "currently open"
            df_kopi = df_kopi[df_kopi['status'] == 'currently open']
    
        vec_calculate_lat_lon_distance = np.vectorize(calculate_lat_lon_distance)
        df_kopi["distance_from_user"] = vec_calculate_lat_lon_distance(df_kopi["lat"], df_kopi["lon"], loc["lat"], loc["lon"])
        df_kopi = df_kopi.sort_values(by="distance_from_user")
        top_10 = df_kopi.head(10)

        top_10["Direction"] = top_10.apply(lambda x: generate_gmaps_direction_url(loc["lat"], loc["lon"], x["lat"], x["lon"]), axis=1)
        top_10["Direction"] = [create_link(url) for url in top_10["Direction"]]
        top_10["search_url"] = top_10.apply(lambda x: generate_gsearch_url(x["name"], x["address"]), axis=1)
        top_10["name_w_url"] = [create_link_with_name(url, name) for url, name in zip(top_10["search_url"], top_10["name"])]
        top_10.to_csv("top_10.csv", index=False)  
        print('top_10["name_w_url"]', top_10["name_w_url"])
        top_10['distance_from_user'] = top_10['distance_from_user'].round(2)
        top_10['distance_from_user'] = top_10['distance_from_user'].astype(float)

        top_10_primary = top_10[["name_w_url","address", "rating", "distance_from_user", "Direction"]]
        top_10_primary.columns = ["Name", "Address", "Rating", "Distance (km)", "Direction (Gmaps)"]
        st.subheader("Here are the Kopi places recommended for you!" + " 🎉")
        fig = go.Figure(
            data=[
                go.Table(
                    # make bigger
                    columnwidth=[100, 200, 100, 100, 200],
                    header=dict(
                        values=[f"<b>{i}</b>" for i in top_10_primary.columns.to_list()],
                        fill_color='white',
                        font_size=15,
                        font_color='black',
                        font_family='Droid Sans',
                        ),
                    cells=dict(
                        values=top_10_primary.transpose()
                        )
                    )
                ]
            )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(
            """
            <div style='
                width: 100%;
                text-align: center;
            '>
                Created by <a href='https://github.com/salmanhiro' target='_blank'>Salman Chen</a>
            </div>
            """,
            unsafe_allow_html=True,
)


if __name__ == "__main__":
    main()