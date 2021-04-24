import streamlit as st
import pandas as pd
import numpy as np
from htbuilder.funcs import rgba, rgb



st.set_page_config(page_title="Covid Dashboard", page_icon="🕸", layout='wide', initial_sidebar_state='expanded')

head , data_info = st.beta_columns(2)

head.title("Covid Dashboard")
data_info.write('Data is obtained from [JHU CSSE COVID-19 Data](https://github.com/CSSEGISandData/COVID-19)')
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

def last_update(data):
  monthDict = {"1":'January', "2":'February',"3": 'March',"4": 'April', "5":'May',"6":'June', "7":'July', "8":'August', "9":'September', "10":'October', "11":'November',"12":'December'}
  last_update = list(data.columns)[-1].split("/")
  last_update = last_update[1]+" "+monthDict[last_update[0]]+" 20"+last_update[-1]
  return last_update

def convert_date(date,option):
    if option == 1:
        monthDict = {"1":'January', "2":'February',"3": 'March',"4": 'April', "5":'May',"6":'June', "7":'July', "8":'August', "9":'September', "10":'October', "11":'November',"12":'December'}
        date=date.split("/")
        date = date[1]+" "+monthDict[date[0]]+" 20"+date[-1]
        return date
    elif option == 2:
        monthDict ={'January':'1','February':'2','March':'3','April':'4','May':'5','June':'6','July':'7','August':'8','September':'9','October':'10','November':'11','December':'12'}
        date=date.split(" ")
        print(date)
        date=monthDict[date[1]]+"/"+date[0]+"/"+date[-1][-2:]
        return date

confirmed = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
death = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
recovered = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

confirmed_update, death_update, recovered_update = st.beta_columns(3)
confirmed_update.write("Confirmed cases last updated on "+last_update(confirmed))
death_update.write("Death cases last updated on "+last_update(death))
recovered_update.write("Recovered cases last updated on "+last_update(recovered))

country_option , empty, date_option  = st.beta_columns(3)

if data_info.checkbox('Show raw data'):
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
else:
  dates = []
  countries = []
  for i in list(confirmed['country/region']):
    if i not in countries:
      countries.append(i)
  country = country_option.selectbox('Please Select the Country',countries,help="Deisplay the data of selcted country")
  for i in list(confirmed[confirmed['country/region']==country].columns)[4:]:
    dates.append(convert_date(i,1))
  date = date_option.select_slider("Select the date", options=dates, value=None,  key=None, help="Select the date to compare deaths, new cases and recovered cases")
  date = convert_date(date,2)
  st.write(f"Total active cases on {date} of {country}: {int(confirmed[confirmed['country/region']==country][date])}")
  
  
  




footer="""<style>
a:link , a:visited{
  color: blue;
  background-color: transparent;
  text-decoration: underline;
}

a:hover,  a:active {
  color: red;
  background-color: transparent;
  text-decoration: underline;
}

.footer {
  position: fixed;
  padding: 10px;
  left: 0;
  bottom: 0;
  width: 100%;
  background-color: white;
  color: black;
  text-align: center;
}
</style>

<div class="footer">
  <p>Developed with ❤ by <a  text-align: center;' href="https://www.heflin.dev/" target="_blank">Heflin Stephen Raj S</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True,)