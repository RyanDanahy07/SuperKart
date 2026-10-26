# Import necessary libraries
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Forecast API")

# Load the trained model pipeline (preprocessing + Random Forest) once at start-up
model = joblib.load("superkart_model.joblib")

# Features the model was trained on, in training order
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Define a route for the home page (GET request)
@superkart_api.get("/")
def home():
    """Simple welcome message to confirm the API is up."""
    return "Welcome to the SuperKart Sales Forecast API!"


# Define an endpoint for single prediction (POST request)
@superkart_api.post("/v1/predict")
def predict_sales():
    """
    Expects a JSON payload with the product and store details listed in FEATURES
    and returns the predicted Product_Store_Sales_Total.
    """
    product_data = request.get_json(silent=True)
    if product_data is None:
        return jsonify({"error": "Request body must be JSON."}), 400

    missing = [f for f in FEATURES if f not in product_data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Build a one-row DataFrame in the training column order
    input_data = pd.DataFrame([{f: product_data[f] for f in FEATURES}])

    # Predict and convert the NumPy float to a Python float so jsonify can serialize it
    prediction = round(float(model.predict(input_data)[0]), 2)

    return jsonify({"Predicted Sales": prediction})


# Define an endpoint for batch prediction (POST request)
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """
    Expects a CSV file (key 'file') with one row per product-store record and
    returns a dictionary of {row index: predicted sales}.
    """
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file under the key 'file'."}), 400

    input_data = pd.read_csv(request.files["file"])

    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    predictions = [round(float(p), 2) for p in model.predict(input_data[FEATURES])]

    # Each key is the row index of the uploaded file
    return jsonify(dict(zip(input_data.index.astype(str), predictions)))


# Run the Flask application in debug mode if this script is executed directly
if __name__ == "__main__":
    superkart_api.run(debug=True)
