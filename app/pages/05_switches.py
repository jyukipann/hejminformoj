import streamlit as st
import requests

left_column, mid_column, right_column = st.columns(3)
env_data = None
red_node_host = 'http://192.168.10.250:1880'
try:
    env_data = requests.get(f"{red_node_host}/dht22").json()
except requests.exceptions.RequestException as e:
    pass
with left_column:
    if st.button("Light on", use_container_width=True):
        ret = requests.get(f"{red_node_host}/light?switch=on")
    if st.button("Night mode", use_container_width=True):
        ret = requests.get(f"{red_node_host}/light?switch=night")
    if st.button("Light off", use_container_width=True):
        ret = requests.get(f"{red_node_host}/light?switch=off")
with mid_column:
    if st.button("PC on", use_container_width=True):
        ret = requests.get(f"{red_node_host}/pc?power=on")
    if st.button("PC off", use_container_width=True):
        ret = requests.get(f"{red_node_host}/pc?power=off")
with right_column:
    label_temp = f"Temp {env_data['temp_c']:.1f}℃" if (
        env_data is not None) else "Refetch Temp"
    label_humid = f"Humid {env_data['humidity']:.1f}%" if (
        env_data is not None) else "Refetch Humid"
    if st.button(label_temp, use_container_width=True):
        st.rerun()
    if st.button(label_humid, use_container_width=True):
        st.rerun()