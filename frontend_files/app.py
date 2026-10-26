import io

import pandas as pd
import requests
import streamlit as st

# Base URL of the Flask backend (container name "backend" on the shared Docker network)
BACKEND_URL = "http://backend:7860"

st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write("Predict the total revenue of a product in a store from its product and store attributes.")

# ---------------- Online prediction ----------------
st.subheader("Online Prediction")

col1, col2 = st.columns(2)
with col1:
    product_weight = st.number_input("Product Weight", min_value=0.0, max_value=50.0, value=12.66, step=0.1)
    product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
    product_area = st.number_input("Product Allocated Area (share of display area)",
                                   min_value=0.0, max_value=1.0, value=0.027, step=0.001, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=1.0)
    product_id_char = st.selectbox("Product Id Prefix", ["FD", "NC", "DR"],
                                   help="FD = food, NC = non-consumable, DR = drinks")
with col2:
    product_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
    store_size = st.selectbox("Store Size", ["Small", "Medium", "High"], index=1)
    store_city = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    store_type = st.selectbox("Store Type",
                              ["Departmental Store", "Supermarket Type1", "Supermarket Type2", "Food Mart"], index=2)
    store_age = st.number_input("Store Age (years)", min_value=0, max_value=100, value=16, step=1)

input_data = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar,
    "Product_Allocated_Area": product_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_city,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": store_age,
    "Product_Type_Category": product_category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=input_data, timeout=30)
        if response.status_code == 200:
            prediction = response.json()["Predicted Sales"]
            st.success(f"Predicted Product-Store Sales Total: {prediction:,.2f}")
        else:
            st.error(f"API error {response.status_code}: {response.text}")
    except requests.exceptions.RequestException:
        st.error("Unable to connect to the prediction API.")

# ---------------- Batch prediction ----------------
st.subheader("Batch Prediction")
uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    if st.button("Predict Batch", type="primary"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/v1/predictbatch",
                files={"file": (uploaded_file.name, file_bytes, "text/csv")},
                timeout=60,
            )
            if response.status_code == 200:
                predictions = response.json()
                results = pd.read_csv(io.BytesIO(file_bytes))
                results["Predicted_Sales"] = [predictions[str(i)] for i in results.index]
                st.success("Batch predictions completed!")
                st.dataframe(results)
            else:
                st.error(f"API error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException:
            st.error("Unable to connect to the prediction API.")
