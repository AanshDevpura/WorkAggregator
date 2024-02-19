'''Data Visualization Dashboard build on a flask backend and d3.js for displays. Currently supports a get command to retrieve time and value data based on a string identifier'''

import os

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@"
    f"{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class AssignmentModel(db.Model):
    """Model for assignments"""
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    due_time = db.Column(db.TIMESTAMP)


@app.route('/')
def index():
    """Render the home page of the application.

    Returns:
        The rendered template for the index.html.
    """
    return render_template('index.html')



@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    """API endpoint to retrieve assignments.

    Returns:
        Flask response: JSON representation of the assignments including names and due times.
    """
    assignments = AssignmentModel.query.all()

    response_data = [{
        "name": assignment.name,
        "due_time": assignment.due_time.isoformat()
    } for assignment in assignments]

    return jsonify(response_data)


@app.route('/api/assignments', methods=['POST'])
def create_assignment():
    """API endpoint to create a new assignment."""
    data = request.json
    name = data.get('name')
    due_time = data.get('due_time')

    if not name or not due_time:
        return jsonify({"error": "Name and due time are required."}), 400

    new_assignment = AssignmentModel(name=name, due_time=due_time)
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({"message": "Assignment created successfully."}), 201


@app.route('/api/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    """API endpoint to delete an assignment."""
    assignment = AssignmentModel.query.get(assignment_id)

    if not assignment:
        return jsonify({"error": "Assignment not found."}), 404

    db.session.delete(assignment)
    db.session.commit()

    return jsonify({"message": "Assignment deleted successfully."})


if __name__ == '__main__':
    app.run(debug=True)