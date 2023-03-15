###Imports
import streamlit as st
import base64
from PIL import Image
import numpy as np
import pydeck as pdk
import pandas as pd
import geopandas as gpd
import seaborn as sns
import math
from modelling.preprocessing.helping_functions import *
from modelling.preprocessing.pre_process_stations import *
from modelling.preprocessing.pre_process_traffic import *
from modelling.models.question_1 import *
from modelling.features.maps import *
import os
import plotly
import plotly.express as px


#import urllib.error

PATH1 = 'data/E-tmja2019-shp/TMJA2019.shp'
PATH2 = 'data/regions-20180101-shp/regions-20180101.shp'
PATH3 = 'data/TCRD_076.xlsx'

PATH_RESULT_30 = 'modelling/results/results_stations_2030_part_3_1.csv'
PATH_RESULT_40 = 'modelling/results/results_stations_2040_part_3_1.csv'

file_list = os.listdir('data/E-tmja2019-shp/')

class Parameters_part_1():
    avg_speed = 80  # km/h
    max_drive_time_daily = 9  # hours
    break_time = 0.33 # hours
    autonomy_daimler = 1000  # km
    autonomy_nikola = 400  # km
    autonomy_daf = 150  # km
    tank_size_daimler = 80
    tank_size_nikola = 32
    tank_size_daf = 30
    capacity_stations = 3*1000

    total_trucks = 10000
    daimler_perc = 0.25
    nikola_perc = 0.25
    daf_perc = 0.50

class Config:
    PATH = '../../data/'

class Params:
    PARAM = 0
config = Config()
p = Params()

### Paths

PATH_BACKGROUND_NOIR = r"noir.jpg"
PATH_LOGO = r"logo.png"

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file,'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def from_data_file(filename):
    url = (
        "http://raw.githubusercontent.com/streamlit/"
        "example-data/master/hello/v1/%s" % filename
    )
    return pd.read_json(url)


def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: scroll;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return


def add_logo_2(png_file):
    '''
    processes the logo 
    '''
    width = 450
    height = 150
    logo = Image.open(png_file)
    modified_logo = logo.resize((width,height))
    return modified_logo


def add_carbon(png_file):
    '''
    processes the logo 
    '''
    width = 200
    height = 200
    logo = Image.open(png_file)
    modified_logo = logo.resize((width,height))
    return modified_logo

def update_sliders(slider1, slider2, slider3):
    total = slider1 + slider2 + slider3
    if total > 100:
        slider1 = 100 - slider2 - slider3
    elif total < 100:
        slider1 = 100 - slider2 - slider3
    return slider1, slider2, slider3


def page_intro():
    '''
    main page with background and sidebar
    '''
    ###Imports
    import streamlit as st
    import webbrowser

    st.markdown('<h1 style="color:white;">Hydrogene truck network optimization Project</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="color:white;">On this page you can test our digital solutions </h3>', unsafe_allow_html=True)
    #background image
    set_png_as_page_bg(PATH_BACKGROUND_NOIR)


    st.markdown('<h4 style="color:white;">The market for hydrogen as a sustainable energy source has been growing rapidly in recent years, with increasing demand for low-emission transportation solutions. France, in particular, has set ambitious targets for reducing carbon emissions and has identified hydrogen as a key part of its strategy to achieve these goals. The country aims to have 6.5 million low-emission vehicles on the road by 2030, with a significant portion powered by hydrogen fuel cells.</h4>', unsafe_allow_html=True)
    st.markdown('<h4 style="color:white;">However, to support the widespread adoption of hydrogen-powered vehicles, a robust infrastructure of hydrogen refueling stations is needed. This is where our project comes in. In this project, we aim to size and optimize the network of hydrogen truck charging stations in France, taking into account various factors such as the forecasted number of hydrogen trucks in France and Europe, truck autonomy, driver regulations, and the motorway network in France.</h4>', unsafe_allow_html=True)
    st.markdown('<h4 style="color:white;">Our project is divided into four parts, each focusing on a specific aspect of the challenge. In the first part, we will analyze the forecasted number of hydrogen trucks in France and Europe and use this information to size the network of hydrogen truck charging stations, including the number of stations and their distribution across different regions of France.</h4>', unsafe_allow_html=True)
    st.markdown('<h4 style="color:white;">In the second part, we will develop models to identify the exact locations where the hydrogen stations should be implemented. These models will consider factors such as truck traffic per transit axis, the localization of logistic hubs, and the cost of deployment and operations per station.</h4>', unsafe_allow_html=True)
    st.markdown('<h4 style="color:white;">In the third part, we will apply these models to France and develop a deployment roadmap for 2030-2040, taking into account three competitive scenarios. These scenarios include a single network in France, two players entering simultaneously, and one player entering after an incumbent transforming its oil stations network to hydrogen.</h4>', unsafe_allow_html=True)
    st.markdown('<h4 style="color:white;">Finally, in the fourth part, we will identify the optimal locations for hydrogen production infrastructure, taking into account factors such as production and transport costs. The output of our project will include geographic repartition models, a deployment roadmap, and the coordinates and types of each station and production plant.</h4>', unsafe_allow_html=True)
    st.markdown('<h3 style="color:white;">This Web App focuses on the two first parts of the project, but tools for part 3 and 4 are in developpement</h3>', unsafe_allow_html=True)
    
    # Add a sidebar to the web page.
    st.markdown('---')
    st.sidebar.image(add_logo_2(PATH_LOGO))
    st.sidebar.markdown('Project led with AirLiquide and the French Ministry of Transports')
    st.sidebar.markdown('We help you develop an hydrogen truck network across France')
    st.sidebar.markdown('---')
    st.sidebar.write('Developped by Group 7')
    st.sidebar.write('**- Cesar Bareau**')
    st.sidebar.write('**- Augustin De La Brosse**')
    st.sidebar.write('**- Alexandra Giraud**')
    st.sidebar.write('**- Camille Keisser**')
    st.sidebar.write('**- Charlotte Simon**')
    st.sidebar.markdown('---')

    st.sidebar.markdown('the link to our work on github is here')
    with st.sidebar:
        if st.button('see our GITHUB'):
            url = 'https://github.com/augustin-delabrosse/sustainability-challenge.git'
            webbrowser.open_new_tab(url)


def page_1():
    '''
    page 1
    '''
    ###Imports
    import streamlit as st
    import base64
    import csv
    import pydeck as pdk
    import folium
    from folium.plugins import HeatMap
    from streamlit_folium import folium_static

    #display
    st.markdown('---')
    st.markdown('<h1 style="color:white;">Market Sizing </h1>', unsafe_allow_html=True)
    set_png_as_page_bg(PATH_BACKGROUND_NOIR)

    with st.sidebar:

        '''
        please choose the repartition of each type of hydrogen truck
        as well as the year of the pediction wanted
        '''

        daimler_perc = st.slider("daimler %", min_value=0, max_value=100, value=33, step = 1)
        daf_perc = st.slider("daf %", min_value=0, max_value=100, value=33, step = 1)
        nikola_perc = st.slider("nikola %", min_value=0, max_value=100, value=33, step = 1)
        daimler_perc, daf_perc, nikola_perc = update_sliders(daimler_perc, daf_perc, nikola_perc)
        year = st.selectbox("select a year",[2030,2040])

        # Read CSV file into a DataFrame and display as table
    if st.button('generate data'):

        #df_traffic = gpd.read_file(config.PATH+'E-tmja2019-shp/TMJA2019.shp')
        df_traffic = gpd.read_file(PATH1)

        # function dans pre_process_traffic.py
        df_traffic = preprocess_data(df_traffic)
        # function dans pre_process_stations.py
        data = add_lat_lon_columns(df_traffic)
        data_r = add_region_column(data)
        # function dans question_1.py.py
        
        #region_data = grouped_region(data_r, config.PATH+'regions-20180101-shp/regions-20180101.shp')
        region_data = grouped_region(data_r, PATH2)

        #df_route_traffic = create_part1_data(config.PATH+"TCRD_076.xlsx", region_data)
        df_route_traffic = create_part1_data(PATH3, region_data)

        # Call your function with the inputs
        output = calculate_hydrogen_stations(df_route_traffic, daimler_perc, nikola_perc, daf_perc,year)
        #st.json(region_data.to_json())

        #capacity_stations = st.slider("Station capacity", min_value=0, max_value=10000, value=3000)
        #demand = st.slider("Demand", min_value=0, max_value=20000, value=10000)

        # Display the output
        st.write("Output:", output)
        mini_region = region_data[['region','geometry']]
        df_heat = mini_region.merge(output,how  = 'left',left_on = 'region',right_on = 'Region')
        #st.write(df_heat)

        # Convert to GeoDataFrame
        gdf = gpd.GeoDataFrame(df_heat, geometry=df_heat['geometry'])
        gdf.set_crs(crs = "epsg:2154",allow_override = True)

        m = folium.Map(location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()],zoom_start=5,tiles='CartoDB positron')
        folium.GeoJson(gdf).add_to(m)

        heat_data = [[row['geometry'].centroid.y, row['geometry'].centroid.x, row['Hydrogen Stations Needed']] for index, row in gdf.iterrows()]
        HeatMap(heat_data, name='Heatmap', min_opacity=0.2, radius=15, blur=10, max_zoom=1).add_to(m)

        folium.LayerControl().add_to(m)
        html_map = folium_static(m)
        st.write(html_map)


#########################################


def page_2():
    '''
    page 2 : Optimise the location of stations with a genetic algorithm
    '''
    ###Imports
    import streamlit as st
    import numpy as np
    import leafmap.foliumap as leafmap
    import folium
    from streamlit_folium import st_folium,folium_static
    #import plotly.express as px
    import pyproj 
    from shapely.geometry import Point
    import seaborn as sns
    from shapely.wkt import loads
    import folium
    #import streamlit_leaflet as stl

    #display
    st.markdown('---')
    st.markdown('<h1 style="color:white;"> Location of future stations</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="color:white;"> Optimisation of the location of stations with a genetic algorithm</h3>', unsafe_allow_html=True)
    set_png_as_page_bg(PATH_BACKGROUND_NOIR)


    liste_infos_additionelles_point = ['index','route','geometry',
        'percentage_traffic', 'Quantity_sold_per_day(in kg)', 'Revenues_day',
        'Quantity_sold_per_year(in kg)', 'station_type','date_installation','Region']

    with st.sidebar:
        '''
        please choose your parameters as well as your constraints
        '''
        #assumptions
        st.markdown('assumptions')
        year = st.selectbox("select a year",[2030,2040])
        hydrogen_price = st.slider("the price of hydrogen [/kg]", min_value=0.0, max_value=15.0, value=3.5, step = 0.5)
        ## constraints
        st.markdown('constraints')
        min_distance_station= st.slider("minimal distance between stations [km]", min_value=10, max_value=1000, value=120, step = 10)
        max_distance_to_hub= st.slider("maximal distance to hub", min_value=0, max_value=100, value=20, step = 10)
        st.markdown('algorithm hyperparameters')
        nb_generation= st.slider("number of generations", min_value=10, max_value=50, value=30, step = 5)
        size_population= st.slider("size of the population", min_value=10, max_value=100, value=50, step = 10)
        
    if st.button('run the genetic algorithm'):
        # Define the style function to color markers based on a column

        # Define the style function to map values to marker colors
        def style_function(feature):
            if feature['properties']['station_type'] == 'large':
                return {'marker_color': 'blue'}
            elif feature['properties']['station_type'] == 'small':
                return {'marker_color': 'red'}
            else:
                return {'marker_color': 'gray'}


        if year == 2030:
            df_results = pd.read_csv(PATH_RESULT_30,usecols=liste_infos_additionelles_point)
            st.dataframe(df_results)

            if type(df_results.geometry[:1].values[0]) == str:
                df_results = convert_str_geometry_to_geometry_geometry(df_results)
        
                stations = gpd.GeoDataFrame(df_results[liste_infos_additionelles_point], 
                                crs="epsg:2154",geometry = 'geometry')

                m = leafmap.Map(center = [49,2.3],zoom = 8)
                m.add_gdf(stations,layer_name = '2030 predictions',style_function = style_function)
                m.to_streamlit()
            
        else:
            df_results = pd.read_csv(PATH_RESULT_40,usecols=liste_infos_additionelles_point)
            st.dataframe(df_results)

            if type(df_results.geometry[:1].values[0]) == str:
                df_results = convert_str_geometry_to_geometry_geometry(df_results)
        
                stations = gpd.GeoDataFrame(df_results[liste_infos_additionelles_point], 
                                crs="epsg:2154",geometry = 'geometry')
                m = leafmap.Map(center = [49,2.3],zoom = 8)
                m.add_gdf(stations,layer_name = '2030 predictions',style_function = style_function)
                m.to_streamlit()


def page_3():
    '''
    page 3: comparaison des differents scenario (1 : monopole, 2: premier acteur mais concurrent, 3: second acteur)
    '''
    ###Imports
    import streamlit as st
    import numpy as np
    import leafmap.foliumap as leafmap
    import folium
    from streamlit_folium import st_folium,folium_static
    #import plotly.express as px
    import pyproj 
    from shapely.geometry import Point
    import seaborn as sns
    from shapely.wkt import loads
    import folium
    #import streamlit_leaflet as stl

    #display
    st.markdown('---')
    st.markdown('<h1 style="color:white;"> Comparaison of different deployement policies </h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="color:white;"> on rapelle les trois scenarios possibles</h3>', unsafe_allow_html=True)
    st.markdown('<h4 style="color:white;"> - scnenario 1 : we are the only provider on the market </h4>', unsafe_allow_html=True)
    st.markdown('<h4 style="color:white;"> - AirLiquide and red team ar enterinf simultaneously on the market with the same level of ambition</h4>', unsafe_allow_html=True)

    
    set_png_as_page_bg(PATH_BACKGROUND_NOIR)



page_names_to_funcs = {
    "Welcome Page": page_intro,
    "Part 1 : Market Sizing ": page_1,
    "Part 2&3 : Optimisation" : page_2,
    "Part 3 : Comparison of different scneratios" : page_2
}

demo_name = st.selectbox("Choose a demo", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()


#if __name__ == __main__():
