import streamlit as st

Lab1 = st.Page("lab1.py",title="First page")
Lab2 = st.Page("lab2.py",title="Second page")
Lab3 = st.Page("lab3.py",title="Third page")
Lab4 = st.Page("lab4.py",title="Fourth Page")
Lab5 = st.Page("lab5.py",title="Fifth Page")

pg = st.navigation([Lab1,Lab2,Lab3,Lab4,Lab5])
st.set_page_config(page_title="Lab5")
pg.run()