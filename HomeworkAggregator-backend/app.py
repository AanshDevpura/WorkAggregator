'''Data Visualization Dashboard build on a flask backend and d3.js for displays. Currently supports a get command to retrieve time and value data based on a string identifier'''

import os
import secrets
import requests

from urllib.parse import urlencode
from flask import Flask, redirect, url_for, render_template, flash, session, current_app, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

app = Flask(__name__, static_folder='static')

#Auth Configs
app.config['OAUTH2_PROVIDERS'] = {
    # GitHub OAuth 2.0 documentation:
    # https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
    'github': {
        'client_id': os.environ.get('GITHUB_CLIENT_ID'),
        'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'userinfo': {
            'url': 'https://api.github.com/user/emails',
            'email': lambda json: json[0]['email'],
        },
        'scopes': ['user:email'],
    },
}

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@"
    f"{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'top secret!'

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'index'


class AssignmentModel(db.Model):
    """Model for assignments"""
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    due_time = db.Column(db.TIMESTAMP)
    
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
  
# Courtesy of https://github.com/miguelgrinberg/flask-oauth-example/blob/main/app.py  
#OAuth2 Endpoint
@app.route('/authorize/<provider>')
def oauth2_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # generate a random string for the state parameter
    session['oauth2_state'] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    qs = urlencode({
        'client_id': provider_data['client_id'],
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
        'response_type': 'code',
        'scope': ' '.join(provider_data['scopes']),
        'state': session['oauth2_state'],
    })

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_data['authorize_url'] + '?' + qs)

@app.route('/callback/<provider>')
def oauth2_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    provider_data = current_app.config['OAUTH2_PROVIDERS'].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if 'error' in request.args:
        for k, v in request.args.items():
            if k.startswith('error'):
                flash(f'{k}: {v}')
        return redirect(url_for('index'))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args['state'] != session.get('oauth2_state'):
        abort(401)

    # make sure that the authorization code is present
    if 'code' not in request.args:
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(provider_data['token_url'], data={
        'client_id': provider_data['client_id'],
        'client_secret': provider_data['client_secret'],
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('oauth2_callback', provider=provider,
                                _external=True),
    }, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get('access_token')
    if not oauth2_token:
        abort(401)

    # use the access token to get the user's email address
    response = requests.get(provider_data['userinfo']['url'], headers={
        'Authorization': 'Bearer ' + oauth2_token,
        'Accept': 'application/json',
    })
    if response.status_code != 200:
        abort(401)
    email = provider_data['userinfo']['email'](response.json())

    # find or create the user in the database
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        user = User(email=email, username=email.split('@')[0])
        db.session.add(user)
        db.session.commit()

    # log the user in
    login_user(user)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

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