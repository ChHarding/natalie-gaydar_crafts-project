import sys
import asyncio

# Fix for Playwright + Streamlit on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
from scraper import scrape_and_analyze
from data_handler import load_data, get_by_user_input
from ui_components import get_project, show_intructions

# MAIN APP
st.title("Craft Today!")

craft_data = load_data()  # Only loads on first run, then cached

if 'show_table' not in st.session_state:
    st.session_state.show_table = False

top_viewed = get_by_user_input(craft_data)

if st.button("Show Projects", type="primary"):
    st.session_state.show_table = True

# Show the table and second button if first button was pressed
if st.session_state.show_table:
    project_title, url = get_project(top_viewed)
    
    if st.button("Get Instructions", type="secondary"):
        st.write(f"Selected project: {project_title}, please be patient while we fetch the instructions...")
        
        try:
            instructions_text = scrape_and_analyze(project_title, url)  # No asyncio.run needed
            show_intructions(project_title, instructions_text)
        except Exception as e:
            st.error(f"Error fetching instructions: {str(e)}")