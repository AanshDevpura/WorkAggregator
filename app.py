import os
import secrets
import requests
import asyncio

from urllib.parse import urlencode
from flask import Flask, redirect, url_for, jsonify, render_template, flash, session, current_app, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from datetime import datetime

import assignments

app = Flask(__name__, static_folder='static')

# Authorization Configs, used to make working with OAuth2 requests easier
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

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@"
    f"{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# A secret key is required for session management
app.config['SECRET_KEY'] = 'top secret!'

db = SQLAlchemy(app)

# Use the login manager to abtract away tracking sessions
login = LoginManager(app)
login.login_view = 'index'

# Table Schema for the assignments table in our database
class AssignmentModel(db.Model):
    """Model for assignments"""
    __tablename__ = 'hwaggregator_usrinfo'
    userid = db.Column(db.String, primary_key=True)
    canvas_credentials = db.Column(db.String)
    moodle_credentials = db.Column(db.String)
    gradescope_credentials = db.Column(db.String)

# Table Schema for the users table in our database
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

# Clear the database and recreate it
@app.route('/clear_database')
def clear_database():
    db.drop_all()
    db.create_all()
    return "Database cleared and recreated."

# Courtesy of https://github.com/miguelgrinberg/flask-oauth-example/blob/main/app.py  
# OAuth2 Endpoint. Redirects the user to the OAuth2 provider's authorization URL to log in
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

# After logging in, the user is redirected to this endpoint. This endpoint exchanges the authorization code for an access token and uses the access token to get the user's email address, and accepts the user into the application
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

# Logout endpoint. Logs the user out of the application
@app.route('/user/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

# Load the user from the database to see if they already exist
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# Our home page. This is the main page of the application on open
@app.route('/')
def index():
    """Render the home page of the application.

    Returns:
        The rendered template for the index.html.
    """
    return render_template('index.html')

def render_schedule(assignments):
    """Render the schedule page of the application.

    Returns:
        The rendered template for the schedule.html.
    """
    
    return render_template('schedule.html', assignments = assignments)

@app.route('/api/v1/addcredentials', methods=['POST'])
def add_credentials():
    """API endpoint to add credentials for a user."""
    app.logger.info('Starting to add credentials')

    if not request.is_json:
        app.logger.warning('Request must be JSON')
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json
    app.logger.info(data)
    userid = data.get('userid')
    platform = data.get('platform')

    if not userid or not platform:
        app.logger.warning('User ID or Platform is missing')
        return jsonify({"error": "User ID or Platform is missing"}), 400

    app.logger.info(f'Received credentials for userid: {userid} on platform: {platform}')

    platform_credentials_field = {
        "canvasForm": "canvas_credentials",
        "moodleForm": "moodle_credentials",
        "gradescopeForm": "gradescope_credentials",
    }

    try:
        access_token = data.get('credentials', {}).get('accesstoken')

        if platform in platform_credentials_field:
            existing_assignment = AssignmentModel.query.filter_by(userid=userid).first()
            credential_field = platform_credentials_field[platform]

            if existing_assignment:
                app.logger.info('Updating existing assignment with new credentials')
                setattr(existing_assignment, credential_field, access_token)
            else:
                app.logger.info('Creating new assignment with credentials')
                new_assignment = AssignmentModel(userid=userid, **{credential_field: access_token})
                db.session.add(new_assignment)

            db.session.commit()
            app.logger.info('Credentials added/updated successfully')
        else:
            app.logger.warning(f'Platform {platform} is not supported')
            return jsonify({"error": f"Platform {platform} is not supported"}), 400

    except Exception as e:
        app.logger.error(f'Error adding/updating credentials: {e}', exc_info=True)
        return jsonify({"error": "An error occurred while processing your request"}), 500

    return jsonify({"received_data": data}), 200

@app.route('/generateschedule/<string:userid>')
async def generate_schedule(userid):
    """API endpoint to generate a schedule for a user. """
    
    # Get credentials from the database
    credentials = AssignmentModel.query.filter_by(userid=userid).first()
    
    canvas_token = credentials.canvas_credentials if credentials and credentials.canvas_credentials else ''
    moodle_token = credentials.moodle_credentials if credentials and credentials.moodle_credentials else ''
    gradescope_user, gradescope_pass = credentials.gradescope_credentials.split(',') if credentials and credentials.gradescope_credentials else ('', '')
    
    canvas_assignments = await assignments.get_canvas_assignments(canvas_token)
    moodle_assignments = await assignments.get_moodle_assignments(moodle_token)
    gradescope_assignments = await assignments.get_gradescope_assignments(gradescope_user, gradescope_pass, False)

    
    # Serialize list of assignments to json
    canvas_assignments = [assignment.to_dict() for assignment in canvas_assignments]
    moodle_assignments = [assignment.to_dict() for assignment in moodle_assignments]
    gradescope_assignments = [assignment.to_dict() for assignment in gradescope_assignments]
    
    all_assignments = sorted(canvas_assignments + moodle_assignments + gradescope_assignments, key=lambda x: datetime.strptime(x['due_date'], '%Y-%m-%d %H:%M:%S'))
    json = {"all": all_assignments}
    return render_schedule(json)
