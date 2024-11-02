import streamlit as st
from tools.simple_auth import check_password
if not check_password():
    st.stop()
    
st.title("Add User")
