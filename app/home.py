import streamlit as st
import requests
st.title("Hejminformoj")
st.write("Hejminformoj is a web application that helps you manage your tasks and time. You can add tasks, start and stop timers, and see the elapsed time for each task.")
left_column, mid_column, right_column = st.columns(3)
temp_data = None
try:
    temp_data = requests.get("http://192.168.10.250:1880/dht22").json()
except requests.exceptions.RequestException as e:
    pass
with left_column:
    if st.button("Light on", use_container_width=True):
        ret = requests.get("http://192.168.10.250:1880/light?switch=on")
    if st.button("Night mode", use_container_width=True):
        ret = requests.get("http://192.168.10.250:1880/light?switch=night")
    if st.button("Light off", use_container_width=True):
        ret = requests.get("http://192.168.10.250:1880/light?switch=off")
with mid_column:
    if st.button("PC on", use_container_width=True):
        ret = requests.get("http://192.168.10.250:1880/pc?switch=on")
    if st.button("PC off", use_container_width=True):
        ret = requests.get("http://192.168.10.250:1880/pc?switch=off")
with right_column:
    if st.button(f"{temp_data['temp_c']}℃" if temp_data is not None else "Refetch Temp", use_container_width=True):
        st.rerun()