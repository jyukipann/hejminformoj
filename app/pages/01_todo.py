import streamlit as st
import requests
from tools.github_api import (
    get_todos_in,
    todo_split_by_status
)

# Streamlitの基本構成
st.title("GitHub Kanban Board")
st.write("Display and manage GitHub Project Board with Streamlit.")
if st.button("Reload"):
    st.write("Reloading...")
    st.rerun()

todo = get_todos_in("LIFE")
todo = todo_split_by_status(todo)

default_titles = ['Todo', 'In Progress', 'Done']
titles = set(todo.keys()) | set(default_titles)
cols = st.columns(len(titles))
non_default_titles = set(titles) - set(default_titles)

def add_todo_column(title:str, todo:dict, col):
    with col:
        st.title(title)
        for t in todo:
            with st.container(border=True):
                st.write(t['title'])
titles = list(todo.keys())

for i, title in zip([0, -2, -1], default_titles):
    add_todo_column(title, todo[title] if title in todo else [], cols[i])

for i, title in enumerate(non_default_titles):
    add_todo_column(title, todo[title], cols[i+1])