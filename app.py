import streamlit as st
import pandas as pd

st.set_page_config(page_title="Covid Dashboard", page_icon="🕸", layout='wide', initial_sidebar_state='expanded')
col1 , col2 ,col3  = st.beta_columns(3)
col1.write('Data is obtained from [JHU CSSE COVID-19 Data](https://github.com/CSSEGISandData/COVID-19)')

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def format_as_indian(value):
    input_list = list(str(value))
    if len(input_list) <= 1:
        formatted_input = value
    else:
        first_number = input_list.pop(0)
        last_number = input_list.pop()
        formatted_input = first_number + ((''.join(l + ',' * (n % 2 == 1) for n, l in enumerate(reversed(input_list)))[::-1] + last_number))
        if len(input_list) % 2 == 0:
            formatted_input.lstrip(',')
    return formatted_input

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
        date=monthDict[date[1]]+"/"+date[0]+"/"+date[-1][-2:]
        return date

def country_wise_data(data,column):
    countries_list = []
    total_cases_list = []
    for i in data["country/region"]:
        if i not in countries_list:
            countries_list.append(i)
            total_cases_list.append(sum(data[data["country/region"] == i][data.columns[-1]]))

    country_wise_total_cases=pd.DataFrame(total_cases_list ,columns=[column], index=countries_list)
    country_wise_total_cases=country_wise_total_cases.sort_values(column,ascending=False)
    for i in country_wise_total_cases.index:
        in_format = format_as_indian(country_wise_total_cases[column][i])
        country_wise_total_cases[column][i] = in_format
    return country_wise_total_cases

confirmed = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
death = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
recovered = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

if last_update(confirmed) == last_update(death) == last_update(recovered):
  col2.write("Data last updated on **"+last_update(confirmed)+"**")
else:  
  confirmed_update, death_update, recovered_update = st.beta_columns(3)
  confirmed_update.write("Confirmed cases last updated on "+last_update(confirmed))
  death_update.write("Death cases last updated on "+last_update(death))
  recovered_update.write("Recovered cases last updated on "+last_update(recovered))

if col3.checkbox('Show raw data'):
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
  col1.subheader("Global cases")
  col1.write(format_as_indian(sum(confirmed[ confirmed.columns[-1]])))
  col2.subheader("Global recoveries")
  col2.write(format_as_indian(sum(recovered[recovered.columns[-1]])))
  col3.subheader("Global deaths")
  col3.write(format_as_indian(sum(death[death.columns[-1]])))

  col1.write(country_wise_data(confirmed,"Cases"))
  col2.write(country_wise_data(recovered,"Recovered"))
  col3.write(country_wise_data(death,"Deaths"))

header = """
<style> 
.header{
    padding: 10px 20px; 
    box-shadow: 0px 2px 2px #c5c5c5;
    left: 0;
    background: white; 
    color: black; 
    position:fixed;
    width: 100%;
    top:0;
    } 
.sticky{ 
    position: fixed; 
    top: 0; 
    width: 100%;
    } 
</style>
<div class="header" >
<p style="font-size:20px">
Covid Dashboard
Developed with ❤ by <a  text-align: center;' href="https://www.heflin.dev/" target="_blank">Heflin Stephen Raj S</a>
<p>
</div>
"""

st.markdown(header, unsafe_allow_html=True)

st.write('Recovered cases for the US are not provided from JHU. [Click here](https://github.com/CSSEGISandData/COVID-19/issues/3464) to read about it.')