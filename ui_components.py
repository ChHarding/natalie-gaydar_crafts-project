import streamlit as st


def get_project(table):
    st.dataframe(table)
    index = st.selectbox("Index:", range(len(table)))
    index_num = int(index)
    
    # Get the project title and Instructables link from the table
    project_title = table.iloc[index_num]['Project-Title']
    instructables_link = table.iloc[index_num]['Instructables-link']
    url = f"https://www.instructables.com{instructables_link}"

    return project_title, url


def show_intructions(project_name, instructions_text):
    st.write(f"Instructions for {project_name}")
    st.text_area("Project Instructions", instructions_text, height=1000, label_visibility="collapsed")