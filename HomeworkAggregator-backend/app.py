'''Data Visualization Dashboard build on a flask backend and d3.js for displays. Currently supports a get command to retrieve time and value data based on a string identifier'''

import os

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# # Database configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@"
#     f"{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
# )
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# class DataModel(db.Model):
#     """Base model for data points, which allows for loose-er coupling for extensibility and testing mocks

#     Attributes:
#         time (db.Column): Timestamp of the data point.
#         value (db.Column): Value of the data point.
#     """
#     __abstract__ = True
#     time = db.Column(db.TIMESTAMP, primary_key=True)
#     value = db.Column(db.Float)
    
# class TemperatureModel(DataModel):
#     __tablename__ = 'CM_HAM_DO_AI1/Temp_value'
#     units = "Celsius"

# class PHModel(DataModel):
#     __tablename__ = 'CM_HAM_PH_AI1/pH_value'
#     units = "pH"

# class OxygenModel(DataModel):
#     __tablename__ = 'CM_PID_DO/Process_DO'
#     units = "%"

# class PressureModel(DataModel):
#     __tablename__ = 'CM_PRESSURE/Output'
#     units = "psi"

@app.route('/')
def index():
    """Render the home page of the application.

    Returns:
        The rendered template for the index.html.
    """
    return render_template('index.html')

# @app.route('/api/data/<string:data_type>', methods=['GET'])
# def get_data(data_type):
#     """API endpoint to retrieve data based on the data type.

#     Args:
#         data_type (str): The type of data to retrieve (e.g., 'temperature').

#     Returns:
#         Flask response: JSON representation of the data including times, values, and units.
#     """
    
#     model_mapping = {
#         "Temperature": TemperatureModel,
#         "PH": PHModel,
#         "Oxygen": OxygenModel,
#         "Pressure": PressureModel
#     }

#     if data_type not in model_mapping:
#         return jsonify({"error": "Invalid data type"}), 400

#     model = model_mapping[data_type]
#     data = db.session.query(model).all()

#     response_data = {
#         "times": [data_point.time.isoformat() for data_point in data],
#         "values": [data_point.value for data_point in data],
#         "units": model.units
#     }

#     return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)