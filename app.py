import streamlit as st
import pandas as pd
import numpy as np
from htbuilder.funcs import rgba, rgb



st.set_page_config(page_title="Covid Dashboard", page_icon="🕸", layout='wide', initial_sidebar_state='expanded')


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


@st.cache
def fetch_data(url):
  data = pd.read_csv(url)
  columns = []
  for i in list(data.columns):
    if i.lower() == "long":
      columns.append("lon")
    else:
      columns.append(i.lower())
  data.columns=columns
  return data

confirmed = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
death = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
recovered = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    option = st.selectbox('Please Select the type of data.',('Confirmed cases', 'Deaths', 'Recovered',"All"))
    if option == 'Confirmed cases':
      st.write(confirmed)
    elif option == "Deaths":
      st.write(death)
    elif option == "Recovered":
      st.write(recovered)
    elif option == "All":
      st.write("Confirmed Case")
      st.write(confirmed)
      st.write("Deaths")
      st.write(death)
      st.write("Recovered")
      st.write(recovered)





st.markdown("""<a style='display: block; text-align: center;' href="https://www.heflin.dev/">Developed with ❤ Heflin Stephen Raj S</a>""",unsafe_allow_html=True,)