import streamlit as st
import requests
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
        ret = requests.get("http://192.168.10.250:1880/pc?power=on")
    if st.button("PC off", use_container_width=True):
        ret = requests.get("http://192.168.10.250:1880/pc?power=off")
with right_column:
    if st.button(f"{temp_data['temp_c']}℃" if temp_data is not None else "Refetch Temp", use_container_width=True):
        st.rerun()