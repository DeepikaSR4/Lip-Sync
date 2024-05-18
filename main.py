import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import date

# Define functions to interact with the database
def create_table():
    conn = sqlite3.connect('study_sessions.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS sessionstable(session TEXT, subject TEXT, description TEXT, session_status TEXT, session_date DATE)')
    conn.commit()
    conn.close()

def add_data(session, subject, description, session_status, session_date):
    conn = sqlite3.connect('study_sessions.db')
    c = conn.cursor()
    c.execute('INSERT INTO sessionstable(session, subject, description, session_status, session_date) VALUES (?, ?, ?, ?, ?)',
              (session, subject, description, session_status, session_date))
    conn.commit()
    conn.close()

def view_all_data():
    conn = sqlite3.connect('study_sessions.db')
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM sessionstable')
        data = c.fetchall()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None
    conn.close()
    return data

def update_data(session, new_subject, new_description, new_session_status, new_session_date):
    conn = sqlite3.connect('study_sessions.db')
    c = conn.cursor()
    c.execute('UPDATE sessionstable SET subject=?, description=?, session_status=?, session_date=? WHERE session=?',
              (new_subject, new_description, new_session_status, new_session_date, session))
    conn.commit()
    conn.close()

def delete_data(session):
    conn = sqlite3.connect('study_sessions.db')
    c = conn.cursor()
    c.execute('DELETE FROM sessionstable WHERE session=?', (session,))
    conn.commit()
    conn.close()

def view_unique_sessions():
    conn = sqlite3.connect('study_sessions.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT session FROM sessionstable WHERE session IS NOT NULL AND session != ""')
    data = c.fetchall()
    conn.close()
    return data

# Main function for Streamlit app
def main():
    st.set_page_config(page_title="Study Session Manager", layout="wide")
    st.title("Stream_Study")

    # Custom CSS for background colors
    st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-color: #D4E6F1; /* Sidebar background color */
    }
    .stButton>button {
        background-color: #4CAF50; 
        color: white; 
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

    menu = ["Create", "Read", "Update", "Delete"]
    choice = st.sidebar.selectbox("Menu", menu)

    create_table()

    if choice == "Create":
        st.subheader("Add Study Session")

        # Layout
        col1, col2 = st.columns(2)

        with col1:
            session = st.text_area("Session Name", placeholder="Enter session name here...")
            subject = st.text_input("Subject", placeholder="Enter subject here...")
            description = st.text_area("Description", placeholder="Enter description here...")

        with col2:
            session_status = st.selectbox("Status", ["Planned", "In Progress", "Completed"])
            session_date = st.date_input("Session Date", date.today())

        if st.button("Add Session"):
            if session and subject and description:  # Ensure fields are not empty
                add_data(session, subject, description, session_status, session_date)
                st.success(f"Successfully Added Study Session: {session}")
            else:
                st.error("All fields must be filled.")

    elif choice == "Read":
        st.subheader("View Study Sessions")
        result = view_all_data()
        if result:
            df = pd.DataFrame(result, columns=['Session', 'Subject', 'Description', 'Status', 'Date'])
            with st.expander("View All Data"):
                st.dataframe(df, height=300)

            with st.expander("Session Status"):
                session_df = df['Status'].value_counts().to_frame().reset_index()
                session_df.columns = ['Status', 'Count']
                st.dataframe(session_df)

                p1 = px.pie(session_df, names='Status', values='Count', title="Session Status Distribution")
                st.plotly_chart(p1, use_container_width=True)
        else:
            st.write("No sessions found.")

    elif choice == "Update":
        st.subheader("Edit/Update Study Sessions")
        result = view_all_data()
        if result:
            df = pd.DataFrame(result, columns=['Session', 'Subject', 'Description', 'Status', 'Date'])
            with st.expander("Current Data"):
                st.dataframe(df, height=300)

            list_of_sessions = [i[0] for i in view_unique_sessions()]
            selected_session = st.selectbox("Select Session", list_of_sessions)
            session_result = [i for i in result if i[0] == selected_session]
            if session_result:
                session = session_result[0][0]
                subject = session_result[0][1]
                description = session_result[0][2]
                session_status = session_result[0][3]
                session_date = pd.to_datetime(session_result[0][4]).date()

                col1, col2 = st.columns(2)

                with col1:
                    new_subject = st.text_input("Subject", subject)
                    new_description = st.text_area("Description", description)
                    new_session_status = st.selectbox("Status", ["Planned", "In Progress", "Completed"], index=["Planned", "In Progress", "Completed"].index(session_status))

                with col2:
                    new_session_date = st.date_input("Session Date", session_date)

                if st.button("Update Session"):
                    update_data(session, new_subject, new_description, new_session_status, new_session_date)
                    st.success(f"Successfully Updated Study Session: {session}")

    elif choice == "Delete":
        st.subheader("Delete Study Sessions")
        result = view_all_data()
        if result:
            df = pd.DataFrame(result, columns=['Session', 'Subject', 'Description', 'Status', 'Date'])
            with st.expander("Current Data"):
                st.dataframe(df, height=300)

            list_of_sessions = [i[0] for i in view_unique_sessions()]
            selected_session = st.selectbox("Select Session", list_of_sessions)
            if st.button("Delete Session"):
                delete_data(selected_session)
                st.success("Study session has been successfully deleted")


if __name__ == '_main_':
    main()