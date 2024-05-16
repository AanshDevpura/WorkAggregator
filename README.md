# Work Aggregator

### Introduction
The website combines upcoming uncompleted Canvas, Moodle, and Gradescopea assignments into a unified schedule, making it easy for University of Illinois Urbana-Champaign students to see what assignments they still need to complete.

### Explanation
The website requires users to log in via Git OAuth2 authentication. This allows them to use previously entered login credentials and API tokens, which are securely stored in a PostgreSQL database and linked to their Git OAuth2. Additionally, users have the flexibility to submit new credentials and API tokens if they need to initialize or update them. Users can then generate a personalized schedule. Leveraging both APIs and web scraping, relevant assignments are fetched and displayed in a scrollable menu interface. This allows users to conveniently view their assignments within the application.

### Installation Instructions
If running for first time on Unix-based systems, you must run this to give the file permission:

chmod +x run-app

Also, you must enter a github client id and corresponding client secret with Homepage URL of http://localhost and Callback URL of http://localhost/callback into the docker-compose file for the Git OAuth2 to work.

This should run the application:

docker-compose up --build

If you need to restart after changes, you can use:

docker-compose down

docker-compose up -d

Once it's running, open up localhost:8888 in a browser
