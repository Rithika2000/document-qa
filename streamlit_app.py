import streamlit as st

create_page = st.Page("lab1.py",title="First page")
delete_page = st.Page("lab2.py",title="Second page")

pg = st.navigation([create_page,delete_page])
st.set_page_config(page_title="Lab2")
pg.run()