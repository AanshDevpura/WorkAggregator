### Project Name
Work Aggregator

### Introduction
Our website combines upcoming uncompleted assignments from Canvas, Moodle, Gradescope, and PrairieLearn into one unified schedule, making it easy for University of Illinois Urbana-Champaign students to see what assignments they still need to complete.

### Technical Architecture
Our website requires users to log in via Git OAuth2 authentication. This allows them to use previously entered login credentials and API tokens, which are securely stored in a PostgreSQL database and linked to their Git OAuth2. Additionally, users have the flexibility to submit new credentials and API tokens if they need to initialize or update them. Users can then generate a personalized schedule. Leveraging both APIs and web scraping techniques, relevant assignments are fetched and displayed in a scrollable menu interface. This allows users to conveniently view their assignments within the application.

### Installation Instructions
If running for first time on Unix-based systems, you must run this to give the file permission:

# Pull the docker image:

docker pull postgres

# Download and add the database:

https://drive.google.com/drive/folders/1OZjmn5yA_LxUZZadwIFSzkjyfqcJGQaG?usp=drive_link
Must be signed into the UIUC google email

chmod +x run-app

docker-compose up --build

This should run the application. If you need to restart after changes, you can use:

docker-compose down

docker-compose up -d

Once it's running, open up localhost:8888 in a browser and there should be some UI showing up

### Group Members and their Roles
Kevin Chen: Implemented Database, Git OAuth2, and most of fullstack.

Aansh Devpura: Implemented fetching Canvas, Moodle, and Gradescope assignments. Also implemented some fullstack modifications.

Abhinav Angirekula: Implemented feteching PrairieLearn assignments.

