import requests
from datetime import datetime
from tzlocal import get_localzone
import pytz
import json
import asyncio
from gradescopecalendar.gradescopecalendar import GradescopeCalendar

class Assignment:
    def __init__(self, course_name, assignment_name, due_date):
        self.course_name = course_name
        self.assignment_name = assignment_name
        self.due_date = due_date

    def to_dict(self):
        return {
            "course_name": self.course_name,
            "assignment_name": self.assignment_name,
            "due_date": self.due_date.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __str__(self):
        return f"Course: {self.course_name}\nAssignment: {self.assignment_name}\nDue Date: {self.due_date.strftime('%Y-%m-%d %H:%M:%S')}"

async def get_canvas_assignments(access_token):
    
    # Headers with authentication
    headers = {
        "Authorization": "Bearer " + access_token
    }

    # Use API to get Canvas assignments
    canvas_assignments_url = "https://canvas.illinois.edu/api/v1//users/self/todo"
    response = requests.get(canvas_assignments_url, headers=headers)

    # Get current date in local timezone
    now = datetime.now(get_localzone())
    
    # Convert assignments to a list of Assignment object
    assignments_list = []
    if response.status_code == 200:
        canvas_assignments = response.json()

        for submission in canvas_assignments:
            assignment = submission["assignment"]
            due_date = datetime.strptime(assignment["due_at"], "%Y-%m-%dT%H:%M:%SZ")
            due_date_utc = due_date.replace(tzinfo=pytz.utc)
            due_date_local = due_date_utc.astimezone(get_localzone())
            if due_date_local > now and assignment['submission_types']!= ['none']:
                assignment_data = Assignment(
                    course_name=submission["context_name"],
                    assignment_name=assignment["name"],
                    due_date=due_date_local
                )
                assignments_list.append(assignment_data)
    return assignments_list

async def get_moodle_assignments(access_token):
    
    # Moodle API parameters
    params = {
        'wstoken': access_token,
        'wsfunction': 'core_calendar_get_action_events_by_timesort',
        'moodlewsrestformat': 'json',
    }

    # Use API to get Moodle assignments
    moodle_assignments_url = 'https://learn.illinois.edu/webservice/rest/server.php'
    response = requests.post(moodle_assignments_url, data=params)
    moodle_assignments = response.json()

    # Get local timezone
    local_tz = get_localzone()

    # Get current date in local timezone
    now = datetime.now(local_tz)

    # Convert assignments to a list of Assignment object
    assignments_list = []
    if 'events' in moodle_assignments:
        for event in moodle_assignments['events']:
            due_date_utc = datetime.fromtimestamp(event['timestart'] + event['timeduration'], tz=pytz.utc)
            due_date_local = due_date_utc.astimezone(local_tz)
            if due_date_local > now and event['action']['name']!= 'View' and event['action']['actionable']== True:
                assignment_data = Assignment(
                    course_name=event['course']['fullname'],
                    assignment_name=event['name'],
                    due_date=due_date_local
                )
                assignments_list.append(assignment_data)
            
    return assignments_list

async def get_gradescope_assignments(email, password, is_instructor):
    
    # Generate calendar
    try:
        calendar = GradescopeCalendar(email, password, is_instructor)
    except Exception as e:
        return []
    calendar._get_calendar_info()
    
    # Fetch assignments from the calendar
    gradescope_assignments = calendar.assignments_all

    # Get local timezone
    local_tz = get_localzone()
    
    # Get current date in local timezone
    now = datetime.now(local_tz)

    # Convert assignments to a list of Assignment objects
    assignments_list = []
    for assignment_name, assignment_details in gradescope_assignments.items():
        due_date = assignment_details.close_date
        due_date_local = due_date.astimezone(local_tz)
        if due_date_local > now and assignment_details.status != 'Submitted':
            assignment_data = Assignment(
                course_name=assignment_details.course.name,
                assignment_name=assignment_details.name,
                due_date=due_date_local
            )
            assignments_list.append(assignment_data)
            
    # Sort assignments by due_date
    assignments_list = sorted(assignments_list, key=lambda x: x.due_date)
    return assignments_list