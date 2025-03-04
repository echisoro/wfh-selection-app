import streamlit as st
import pandas as pd
import os
import xlsxwriter
from datetime import datetime, timedelta

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
        df = pd.read_csv(data_file)
        # Ensure required columns exist
        expected_columns = ["Name", "Week", "Week Starting", "Day", "WFH Date"]
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None  # Add missing columns if needed
        return df
    return pd.DataFrame(columns=["Name", "Week", "Week Starting", "Day", "WFH Date"])

def save_data(df):
    df.to_csv(data_file, index=False)

data = load_data()

# Streamlit UI
st.title("🏠 Work From Home Selection")
st.write("📅 Select your Work From Home day for the current week.")

# Get current week number, year, and Monday date
current_week = datetime.today().strftime("%Y-%W")
week_start = (datetime.today() - timedelta(days=datetime.today().weekday())).date()
st.subheader(f"📆 Current Week Selections (Week Starting {week_start.strftime('%d %B %Y')})")

# Function to calculate WFH Date based on selection
def get_wfh_date(selected_day, week_start):
    if selected_day == "Thursday":
        return week_start + timedelta(days=3)
    elif selected_day == "Friday":
        return week_start + timedelta(days=4)
    return None

# Selection form
with st.form("wfh_form"):
    name = st.selectbox("👤 Select your name", staff_members)
    day = st.radio("📌 Choose your WFH day", ["Thursday", "Friday"])
    submit = st.form_submit_button("✅ Submit")
    
    if submit:
        wfh_date = get_wfh_date(day, week_start)
        existing_entry = data[(data["Name"] == name) & (data["Week"] == current_week)]
        if not existing_entry.empty:
            st.warning("⚠️ You have already selected a day for this week.")
        else:
            new_entry = pd.DataFrame({
                "Name": [name], "Week": [current_week], "Week Starting": [week_start], "Day": [day], "WFH Date": [wfh_date]
            })
            data = pd.concat([data, new_entry], ignore_index=True)
            save_data(data)
            st.success(f"🎉 {name} selected {day} for WFH this week.")
            st.rerun()

# Display current week's selections
current_week_data = data[data["Week"] == current_week]
st.dataframe(current_week_data)

# Add Reset Data Button with Authentication
password = st.text_input("🔑 Enter Admin Password to Reset Data:", type="password")
if st.button("🗑️ Reset Data"):
    if password == "tamuda":
        if os.path.exists(data_file):
            os.remove(data_file)
        data = pd.DataFrame(columns=["Name", "Week", "Week Starting", "Day", "WFH Date"])
        save_data(data)
        st.success("🔄 All previous selections have been cleared!")
        st.rerun()
    elif password:
        st.error("❌ Incorrect password! Data reset not allowed.")

# Download options
st.subheader("📥 Download Data")
file_format = st.radio("📝 Select format", ["CSV", "Excel", "Text"], horizontal=True)

def convert_to_file(format):
    download_data = data[["Week", "Week Starting", "Name", "Day", "WFH Date"]]
    download_date = datetime.today().strftime("%Y-%m-%d")
    if format == "CSV":
        return download_data.to_csv(index=False).encode('utf-8'), f"wfh_selections_{download_date}.csv"
    elif format == "Excel":
        excel_file = f"wfh_selections_{download_date}.xlsx"
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            download_data.to_excel(writer, index=False, sheet_name="WFH Data")
        with open(excel_file, "rb") as f:
            return f.read(), excel_file
    else:
        text_data = download_data.to_string(index=False)
        return text_data.encode('utf-8'), f"wfh_selections_{download_date}.txt"

if st.button("📂 Download"):
    file_content, file_name = convert_to_file(file_format)
    st.download_button("📥 Download File", file_content, file_name)
