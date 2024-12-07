from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import os
from .helpers import predict_shelf_life
from .models import predict_image
from . import mongo

# Blueprint definition
main = Blueprint('main', __name__)

# Constants
UPLOAD_FOLDER = os.path.join('Backend','app', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@main.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')


@main.route('/predict', methods=['POST'])
def predict():
    """
    Handle file uploads and predict the shelf life of the uploaded fruit or vegetable image.
    """
    try:
        # Ensure a file is provided
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if not file:
            return jsonify({"error": "No file provided"}), 400

        # Save the file to the upload folder
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Predict the class of the image
        predicted_class = predict_image(filepath)
        if not predicted_class:
            return jsonify({"error": "Prediction failed"}), 500

        # Extract category and fruit name
        category, fruit = predicted_class.split(' ', 1)

        # Parse the temperature input
        try:
            temperature = float(request.form['temperature']) + 273.15
        except (KeyError, ValueError):
            return jsonify({"error": "Invalid temperature value"}), 400

        # Prepare the database record
        life=0 if category == "Bad" else predict_shelf_life(predicted_class, temperature)
        record = {
            "timestamp": datetime.now(),
            "temperature": round(temperature - 273.15, 2),
            "shelf_life": life,
            "category": category,
            "fruitname": fruit
        }

        # Insert the record into the database
        try:
            print("MongoDB instance:", mongo.db)
            mongo.db.predictions.insert_one(record)
        except Exception as db_error:
            print("insertion error: ",str(db_error))
            return jsonify({
                "error": "Database insertion failed",
                "details": str(db_error)
            }), 500

        # Prepare and return response
        response = {
            "life": life,
            "name": fruit,
            "category": category
        }

        return jsonify(response)

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500


