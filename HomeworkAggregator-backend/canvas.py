import requests
from datetime import datetime
import json

# Canvas API URL
API_URL = "https://canvas.illinois.edu/api/v1/"

def get_access_token():
    # Prompt the user to enter their Canvas access token
    access_token = input("Please enter your Canvas access token: ")
    return access_token

def get_canvas_assignments(access_token):
    # Get current date
    now = datetime.now()
    
    # API endpoint for Canvas assignments
    canvas_assignments_url = f"{API_URL}/users/self/todo"
    
    # Headers with authentication
    headers = {
        "Authorization": "Bearer " + access_token
    }
    
    response = requests.get(canvas_assignments_url, headers=headers)
    
    if response.status_code == 200:
        canvas_assignments = response.json()
        assignments = []

        for submission in canvas_assignments:
            assignment = submission["assignment"]
            due_date = datetime.strptime(assignment["due_at"], "%Y-%m-%dT%H:%M:%SZ")
            if due_date > now:
                # Store assignment as a list
                assignment_info = {
                    "course_name" : submission["context_name"],
                    "assignment_name" : assignment["name"],
                    "due_date" : due_date.strftime('%Y-%m-%d %H:%M:%S')  # Convert due_date to string
                }
                assignments.append(assignment_info)
        return assignments
    else:
        print(f"Error fetching Canvas assignments. Status code: {response.status_code}")
        return None

def save_to_json(data):
    with open('canvas_assignments.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    access_token = get_access_token()
    canvas_assignments = get_canvas_assignments(access_token)

    if canvas_assignments:
        print("Canvas Assignments:")
        for assignment in canvas_assignments:
            print(assignment)
        
        # Save assignments to JSON file
        save_to_json(canvas_assignments)
        print("Canvas assignments saved to 'canvas_assignments.json'")
    else:
        print("Failed to fetch Canvas assignments.")
