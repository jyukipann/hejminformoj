import streamlit as st
from tools.db_init import get_engine

st.title("Hejminformoj")
st.markdown(
"""
Hejminformoj estas programo por multaj funkcioj.
Ekzemple, hejma buĝeto, todo-listo, kaj panelo por regi inteligentan hejmon.
Ĝi estas tre utila, ĉu ne?
## Funkcioj
- todo
- Kalkulilo de hejma buĝeto
    - Aldoni
    - Montri
- Panelo por regi inteligentan hejmon
"""
)