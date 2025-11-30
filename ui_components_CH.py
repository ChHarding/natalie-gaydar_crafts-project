import streamlit as st


def get_project(table):
    # Display table with row selection enabled
    event = st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="project_table"
    )
    
    # Get the selected row index
    if event.selection.rows:
        selected_idx = table.index[event.selection.rows[0]]
    else:
        selected_idx = table.index[0]  # Default to first row if none selected
    
    # Get the project title and Instructables link from the selected row
    project_title = table.loc[selected_idx, 'Project-Title']
    instructables_link = table.loc[selected_idx, 'Instructables-link']
    url = f"https://www.instructables.com{instructables_link}"

    return project_title, url


def show_intructions(project_name, instructions_text):
    st.write(f"Instructions for {project_name}")
    st.text_area("Project Instructions", instructions_text, height=1000, label_visibility="collapsed")