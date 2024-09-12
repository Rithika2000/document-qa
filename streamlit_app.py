import streamlit as st

Lab1 = st.Page("lab1.py",title="First page")
Lab2 = st.Page("lab2.py",title="Second page")
Lab3 = st.Page("lab3.py",title="Third page")

pg = st.navigation([Lab1,Lab2,Lab3])
st.set_page_config(page_title="Lab3")
pg.run()