import streamlit as st
import pandas as pd

# Set the title of the application
st.title("Budget Data Viewer")

# --- Code to handle the file upload ---
# You have two main options for hosting your data on Streamlit Cloud:

# Option 1 (Recommended for Streamlit Cloud): Read the file from your GitHub repository
# When you deploy your app on Streamlit Cloud, it's best practice to include your 
# data files (like Budget.csv) in the same GitHub repository as your Python script.
# You can then read the file directly using its relative path.
try:
    # Assuming 'Budget.csv' is in the same directory as 'app.py'
    file_path = "Budget.csv"
    df = pd.read_csv(file_path)
    st.success(f"Successfully loaded data from the file: {file_path}")

except FileNotFoundError:
    st.error("Error: 'Budget.csv' not found. Please ensure it is in the same directory as your Streamlit script.")
    st.info("If you are testing locally, make sure Budget.csv is in the current folder.")
    # Stop the app execution if the file is not found
    st.stop()

except Exception as e:
    st.error(f"An error occurred while reading the CSV file: {e}")
    st.stop()


# --- Display the data ---

st.header("1. Data Summary")
st.write(f"The dataset has {df.shape[0]} rows and {df.shape[1]} columns.")
st.subheader("First 5 Rows")
st.dataframe(df.head()) # Use st.dataframe for an interactive table

st.header("2. Full Dataset")
# Display the entire DataFrame as an interactive table
st.dataframe(df)

# --- End of Streamlit script ---
