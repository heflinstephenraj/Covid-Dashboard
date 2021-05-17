from hashlib import new
from os.path import join
from time import time_ns
from altair.vegalite.v4.schema.channels import Color
import numpy as np
from fake_useragent.utils import get
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import requests
import datetime 
from fake_useragent import UserAgent

st.set_page_config(page_title="Covid Dashboard", page_icon="🕸", layout='wide', initial_sidebar_state='expanded')

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


pd.options.mode.chained_assignment=None

option_1,option_2,option_3 = "Covid Global dashboard","Covid Vaccination (India)","Covid Inida dashboard"
dashboard_options = st.sidebar.selectbox(
    "How would you like to be contacted?",
    (option_1,option_2,option_3)
)

if dashboard_options == option_1:
  st.title("Covid Dashboard")
  column_1 , column_2 , column_3 , column_4 = st.beta_columns((2, 1, 1, 1))
  col1 , col2 ,col3  = st.beta_columns(3)
  st.sidebar.write('Developed with ❤ by [Heflin Stephen Raj S](https://www.heflin.dev/)')
  st.sidebar.write('Data is obtained from [JHU](https://github.com/CSSEGISandData/COVID-19)')


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
    if i.lower() == "long" or i.lower() == "long_":
      columns.append("lon")
    else:
      columns.append(i.lower())
  data.columns=columns
  return data

def last_update(data,option=1):
  
  monthDict = {"1":'January', "2":'February',"3": 'March',"4": 'April', "5":'May',"6":'June', "7":'July', "8":'August', "9":'September', "10":'October', "11":'November',"12":'December'}
  if option == 1:
    last_update = list(data.columns)[-1].split("/")
    last_update = last_update[1]+" "+monthDict[last_update[0]]+" 20"+last_update[-1]
    return last_update
  else:
    month=data.split("-")[0]
    if len(data.split("-")[-1]) == 4:
      last_update = data.split("-")[1]+" "+monthDict[str(int(month))]+" "+data.split("-")[-1]
    else:  
      last_update = data.split("-")[1]+" "+monthDict[str(int(month))]+" 20"+data.split("-")[-1]
    return last_update

def get_vaccination(date,pincode,fee,age):
  if age == '18-45':
    age_select = 18
  else:
    age_select = 45
  date=str(date).split("-")
  date=date[-1]+"-"+date[1]+"-"+date[0]
  ua = UserAgent()
  header = {'User-Agent':str(ua.chrome)}
  try:
    data=requests.get(f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode={pincode}&date={date}",headers=header)
    data = data.json()
  except:
    st.warning("Heroku requires Credit card details to use User-Agent in requesting the data from Cowin API. So Vaccination functionality is not available on the live website, But It works fine on the local machine.")
    return "No"
  if not data["sessions"]:
    return "No"
  final = []
  for i in data["sessions"]:
    if fee != "All":
      if i["fee_type"] ==fee and i["min_age_limit"] == age_select:
        add={"Name":i["name"],"Vaccine":i["vaccine"],"Fee":i["fee"],"Available capacity":i["available_capacity"],"From":str(i["from"])[:-3],"To":str(i["to"])[:-3],"Slots":i["slots"],"Address":i["address"]+", "+i["district_name"]+", "+i["state_name"]}
        final.append(add)
    else:
      if  i["min_age_limit"] == age_select:
        add={"Name":i["name"],"Vaccine":i["vaccine"],"Fee":i["fee"],"Available capacity":i["available_capacity"],"From":str(i["from"])[:-3],"To":str(i["to"])[:-3],"Slots":i["slots"],"Address":i["address"]+", "+i["district_name"]+", "+i["state_name"]}
        final.append(add)
  if not final:
    return "No"
  return final
  

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
    country_wise_total_cases["Countries"] = country_wise_total_cases.index
    country_wise_total_cases=country_wise_total_cases.sort_values(column,ascending=False)
    country_wise_total_cases.index = range(1,len(country_wise_total_cases)+1)
    first_column = country_wise_total_cases.pop(column)
    country_wise_total_cases.insert(1, column, first_column)
    for i in country_wise_total_cases.index:
        in_format = format_as_indian(country_wise_total_cases[column][i])
        country_wise_total_cases[column][i] = in_format
    return country_wise_total_cases

if dashboard_options == option_1 or dashboard_options == option_3:
  confirmed = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
  death = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
  recovered = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

if dashboard_options == option_1:
  if last_update(confirmed) == last_update(death) == last_update(recovered):
    st.sidebar.write("Last updated: **"+last_update(confirmed)+"**")
  else:  
    confirmed_update, death_update, recovered_update = st.beta_columns(3)
    st.sidebar.write("Confirmed cases last updated on "+last_update(confirmed))
    st.sidebar.write("Death cases last updated on "+last_update(death))
    st.sidebar.write("Recovered cases last updated on "+last_update(recovered))


  col1.subheader("Global cases")
  col1.write(format_as_indian(sum(confirmed[ confirmed.columns[-1]])))
  col2.subheader("Global recoveries")
  col2.write(format_as_indian(sum(recovered[recovered.columns[-1]])))
  col3.subheader("Global deaths")
  col3.write(format_as_indian(sum(death[death.columns[-1]])))

  col1.write(country_wise_data(confirmed,"Cases"))
  col2.write(country_wise_data(recovered,"Recoveries"))
  col3.write(country_wise_data(death,"Deaths"))

  st.sidebar.write('Recovered cases for the US are not provided from JHU. [Click here](https://github.com/CSSEGISandData/COVID-19/issues/3464) to read about it.')


if dashboard_options == option_2:
  st.title(option_2)
  st.sidebar.write('Developed with ❤ by [Heflin Stephen Raj S](https://www.heflin.dev/)')
  
  col1 , col2 ,col3, col4  = st.beta_columns(4)
  
  pincode = col3.text_input("Enter the pincode","600071")
  date=col1.date_input("Select the date")
  fee=col2.radio("Fees type",["All","Free","Paid"])
  age = col4.radio('Age limit',('45+','18-45'))
  vaccination=get_vaccination(date,pincode,fee,age)

  if vaccination == "No":
    if fee == "All":
      st.warning(f"No vaccination centers are avaliable for {age} years old people at {pincode} on {date}.")
    else:
      st.warning(f"No {fee.lower()} vaccination centers are avaliable for {age} years old people at {pincode} on {date}.")
  else:
    name,vaccine,fee,available,fr,to,slots,address=st.beta_columns(( 2, 1, 1,1,1,1,3,3))
    name.subheader("Name")
    vaccine.subheader("Vaccine")
    fee.subheader("Fee")
    available.subheader("Available")
    fr.subheader("From")
    to.subheader("To")
    slots.subheader("Slots")
    address.subheader("Address")
    for i in vaccination:
      available.text(i["Available capacity"])
      fr.text(i["From"])
      to.text(i["To"])
      time_slot=""
      for j in i["Slots"]:
        if j == i["Slots"][0]:
          time_slot = j
        else:
          time_slot=time_slot+", "+j
      slots.text(time_slot)
      fee.text(i["Fee"])
      name.text(i["Name"])
      vaccine.text(i["Vaccine"])
      address.text(i["Address"])
      
if dashboard_options == option_3:
  st.title("Covid India dashboard")
  st.sidebar.write('Developed with ❤ by [Heflin Stephen Raj S](https://www.heflin.dev/)')
  
  #Confirmed New Cases
  confirmed = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
  confirmed_india=confirmed[confirmed["country/region"]=="India"]
  orginal_confirmed_column = list(confirmed_india.columns)[-60:]  
  data=confirmed_india[orginal_confirmed_column].T
  data.columns = ["Confirmed"]
  last=list(confirmed.columns[-60:])
  new_case_list=[]
  for i in range(len(orginal_confirmed_column)):
      if last[0]==orginal_confirmed_column[i]:
          add_date=orginal_confirmed_column[i-1]
  for i in range(len(last)):
      if i == 0:
          columns = list(confirmed.columns)
          for j in range(len(columns)):
            if columns[j] == last[0]:
              new_case=int(abs(confirmed[confirmed["country/region"]=="India"][columns[j-1]]-confirmed_india[last[0]]))
              new_case_list.append({"New cases":new_case})
      else:
          new_case=int(abs(data.loc[last[i-1]]-data.loc[last[i]]))
          new_case_list.append({"New cases":new_case})
  new_cases_data=pd.DataFrame(new_case_list,index=last)
  new_cases_data.index= pd.to_datetime(new_cases_data.index)

  #Recovered New cases
  recovered = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
  recovered_india=recovered[recovered["country/region"]=="India"]
  orginal_confirmed_column = list(recovered_india.columns)[-60:]
  data=recovered_india[orginal_confirmed_column].T
  data.columns = ["recovered"]
  last=list(recovered.columns[-60:])
  new_case_list=[]
  for i in range(len(last)):
      if i == 0:
          columns = list(recovered.columns)
          for j in range(len(columns)): 
              if columns[j] == last[0]:
                  new_case=int(abs(recovered[recovered["country/region"]=="India"][columns[j-1]]-recovered_india[last[0]]))
                  new_case_list.append({"New recovered cases":new_case})
      else:
          new_case=int(abs(data.loc[last[i-1]]-data.loc[last[i]]))
          new_case_list.append({"New recovered cases":new_case})
  new_recovered_data=pd.DataFrame(new_case_list,index=last)
  new_recovered_data.index= pd.to_datetime(new_recovered_data.index)

  #Death New cases
  deaths = fetch_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
  deaths_india=deaths[deaths["country/region"]=="India"]
  orginal_confirmed_column = list(deaths_india.columns)[-60:]
  data=deaths_india[orginal_confirmed_column].T
  data.columns = ["Deaths"]
  last=list(confirmed.columns[-60:])
  new_case_list=[]
  for i in range(len(orginal_confirmed_column)):
      if last[0]==orginal_confirmed_column[i]:
          add_date=orginal_confirmed_column[i-1]
  for i in range(len(last)):
      if i == 0:
          columns = list(deaths.columns)
          for j in range(len(columns)):
            if columns[j] == last[0]:
              new_case=int(abs(deaths[deaths["country/region"]=="India"][columns[j-1]]-deaths_india[last[0]]))
              new_case_list.append({"New Deaths":new_case})
      else:
          new_case=int(abs(data.loc[last[i-1]]-data.loc[last[i]]))
          new_case_list.append({"New Deaths":new_case})
  new_deaths_data=pd.DataFrame(new_case_list,index=last)
  new_deaths_data.index= pd.to_datetime(new_cases_data.index)

  col1,col2,col3=st.beta_columns(3)
  col1.subheader("Confirmed cases")
  col1.write(format_as_indian(int(confirmed[confirmed["country/region"]=="India"][confirmed.columns[-1]])))
  col2.subheader("Recoveries")
  col2.write(format_as_indian(int(recovered[recovered["country/region"]=="India"][recovered.columns[-1]])))
  col3.subheader("Deaths")
  col3.write(format_as_indian(int(death[death["country/region"]=="India"][death.columns[-1]])))
  col1.subheader("New confirmed cases")
  col1.write(format_as_indian(int(new_cases_data.loc[new_cases_data.index[-1]])))
  col2.subheader("New deaths")
  col2.write(format_as_indian(int(new_deaths_data.loc[new_deaths_data.index[-1]])))
  col3.subheader("New recoveries")
  col3.write(format_as_indian(int(new_recovered_data.loc[new_recovered_data.index[-1]])))


  
  st.write(f"New confirmed cases from {last[0]} to {last[-1]} (60 days)")
  chart = st.line_chart(new_cases_data)

  
  st.write(f"New deaths from {last[0]} to {last[-1]} (60 days)")
  chart = st.line_chart(new_deaths_data)

  
  st.write(f"New recovered cases from {last[0]} to {last[-1]} (60 days)")
  chart = st.line_chart(new_recovered_data)
  try:
    date=str(datetime.datetime.now()).split(" ")[0].split("-")
    date=date[1]+"-"+date[-1]+"-"+date[0]
    url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date}.csv"
    data=fetch_data(url)
  except:
    date=str(datetime.datetime.now()).split(" ")[0].split("-")
    if len(str(int(date[-1])+1)) == 1:
        date=str(date[1])+"-"+"0"+str(int(date[-1])+1)+"-"+str(date[0])
    else:    
        date=str(date[1])+"-"+str(int(date[-1])-1)+"-"+str(date[0])
    url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date}.csv"
    data=fetch_data(url)
    data=data[data["country_region"]=="India"]
    data=data.sort_values(by="confirmed",ascending=False)
    states=st.multiselect("Select States",list(data["province_state"]),default=list(data["province_state"])[:5])
    state_data=[]
    for i in states:
      for j in range(len(data)):
        if i == data.iloc[j]["province_state"]:
          state_data.append(dict(data.iloc[j]))
    state_data=pd.DataFrame(state_data).sort_values("confirmed",ascending=False)

    st.sidebar.write(f"Last Updated: **{last_update(date,2)}**")
    st.sidebar.write('Data is obtained from [JHU](https://github.com/CSSEGISandData/COVID-19)')
    if states:
      viz1,viz2=st.beta_columns(2)
      fig = px.pie(state_data, values=state_data['confirmed'], names=state_data['province_state'], title=f'Total Confirmed Cases of {last_update(date,2)}',width=500,height=500)
      viz2.plotly_chart(fig)
      layout = go.Layout(autosize=False,width=500,height=500,xaxis= go.layout.XAxis(linecolor = 'black',linewidth = 1,mirror = True),yaxis= go.layout.YAxis(linecolor = 'black',linewidth = 1,mirror = True),margin=go.layout.Margin(l=50,r=50,b=100,t=100,pad = 4))
      fig = go.Figure(data=[
        go.Bar(name='Confirmed', x=state_data['province_state'], y=state_data['confirmed']),
        go.Bar(name='Recovered', x=state_data['province_state'], y=state_data['recovered']),
        go.Bar(name='Active', x=state_data['province_state'], y=state_data['active'])],
        layout=layout)
      fig.update_layout(
        title=f'Comparison of {last_update(date,2)}',
        xaxis_tickfont_size=12,
        yaxis=dict(title="No. of people",titlefont_size=16,tickfont_size=14,),
        legend=dict(x=0.70,y=1.00),
        barmode='group',
        bargap=0.15, 
        bargroupgap=0.1)
      viz1.plotly_chart(fig)