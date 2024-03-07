import requests
from datetime import datetime
from tzlocal import get_localzone
import pytz
import json

def get_canvas_token():
    canvas_token = input("Please enter your Canvas access token: ")
    return canvas_token

def get_canvas_assignments(access_token):
    
    # Headers with authentication
    headers = {
        "Authorization": "Bearer " + access_token
    }

    # Use API to get Canvas assignments
    canvas_assignments_url = "https://canvas.illinois.edu/api/v1//users/self/todo"
    response = requests.get(canvas_assignments_url, headers=headers)

    # Get current date in local timezone
    now = datetime.now(get_localzone())
    
    # Convert assignments to a list of dictionaries
    assignments_list = []
    if response.status_code == 200:
        canvas_assignments = response.json()

        for submission in canvas_assignments:
            assignment = submission["assignment"]
            due_date = datetime.strptime(assignment["due_at"], "%Y-%m-%dT%H:%M:%SZ")
            due_date_utc = due_date.replace(tzinfo=pytz.utc)
            due_date_local = due_date_utc.astimezone(get_localzone())
            if due_date_local > now:
                assignment_data = {
                    "course_name": submission["context_name"],
                    "assignment_name": assignment["name"],
                    "due_date": due_date_local.strftime("%Y-%m-%d %H:%M:%S")
                }
                assignments_list.append(assignment_data)
    return assignments_list

def get_moodle_token():
    moodle_token = input("Please enter your Moodle access token: ")
    return moodle_token


def get_moodle_assignments(access_token):
    
    # Moodle API parameters
    params = {
        'wstoken': access_token,
        'wsfunction': 'core_calendar_get_calendar_upcoming_view',
        'moodlewsrestformat': 'json',
    }

    # Use API to get Moodle assignments
    moodle_assignments_url = 'https://learn.illinois.edu/webservice/rest/server.php'
    response = requests.post(moodle_assignments_url, data=params)
    moodle_assignments = response.json()

    # Get local timezone
    local_tz = get_localzone()

    # Convert assignments to a list of dictionaries
    assignments_list = []
    if 'events' in moodle_assignments:
        for event in moodle_assignments['events']:
            try:
                course = event['course']['fullname']
            except:
                course = "N/A"

            due_date_utc = datetime.fromtimestamp(event['timestart'] + event['timeduration'], tz=pytz.utc)
            due_date_local = due_date_utc.astimezone(local_tz)

            assignment = {
                'course_name': course,
                'assignment_name': event['name'],
                "due_date": due_date_local.strftime('%Y-%m-%d %H:%M:%S')
            }
            assignments_list.append(assignment)
            
    return assignments_list

def get_assignments():
    # Get Canvas API token
    canvas_token = get_canvas_token()

    # Get Canvas assignments
    try:
        canvas_assignments = get_canvas_assignments(canvas_token)
    except Exception as e:
        canvas_assignments = []

    # Get Moodle API token
    moodle_token = get_moodle_token()

    # Get Moodle assignments
    try:
        moodle_assignments = get_moodle_assignments(moodle_token)
    except Exception as e:
        moodle_assignments = []

    combined_assignments = sorted(canvas_assignments + moodle_assignments, key=lambda x: x["due_date"])
    
    # Convert to JSON
    json_data = json.dumps(combined_assignments, indent=4)
    
    # Print or return the JSON data
    print(json_data)

    # If you want to return instead of print, use the following line
    # return json_data

get_assignments()


