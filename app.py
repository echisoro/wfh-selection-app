import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File to store selections
data_file = "wfh_selections.csv"

# Staff members
staff_members = [
    "Helene Niemann", "Edward Chisoro", "Rodrick Sinamano",
    "Thokozile Mokhele", "Marie Ayaba", "Olivia Dlamini", "Karabo Kotu"
]

# Load or create data file
def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    return pd.DataFrame(columns=["Name", "Week", "Day", "Date"])

def save_data(df):
    df.to_csv(data_file, index=False)

data = load_data()

# Streamlit UI
st.title("Work From Home Selection")
st.write("Select your Work From Home day for the current week.")

# Get current week number and year
current_week = datetime.today().strftime("%Y-%W")

# Selection form
with st.form("wfh_form"):
    name = st.selectbox("Select your name", staff_members)
    day = st.radio("Choose your WFH day", ["Thursday", "Friday"])
    submit = st.form_submit_button("Submit")
    
    if submit:
        existing_entry = data[(data["Name"] == name) & (data["Week"] == current_week)]
        if not existing_entry.empty:
            st.warning("You have already selected a day for this week.")
        else:
            new_entry = pd.DataFrame({
                "Name": [name], "Week": [current_week], "Day": [day], "Date": [datetime.today().date()]
            })
            data = pd.concat([data, new_entry], ignore_index=True)
            save_data(data)
            st.success(f"{name} selected {day} for WFH this week.")

# Display current week's selections
st.subheader("Current Week Selections")
current_week_data = data[data["Week"] == current_week]
st.dataframe(current_week_data)

# Display all past selections
st.subheader("All Past Selections")
st.dataframe(data)

# Download options
st.subheader("Download Data")
file_format = st.radio("Select format", ["CSV", "Excel", "Text"], horizontal=True)

def convert_to_file(format):
    if format == "CSV":
        return data.to_csv(index=False).encode('utf-8'), "wfh_selections.csv"
    elif format == "Excel":
        excel_file = "wfh_selections.xlsx"
        data.to_excel(excel_file, index=False)
        return excel_file, "wfh_selections.xlsx"
    else:
        text_data = data.to_string(index=False)
        return text_data.encode('utf-8'), "wfh_selections.txt"

if st.button("Download"):
    file_content, file_name = convert_to_file(file_format)
    st.download_button("Download File", file_content, file_name)
