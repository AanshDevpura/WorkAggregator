To build the application for the first time, run:

chmod +x run-app

docker-compose up --build

This should run the applciation. If you need to restart after changes, you can use:

docker-compose down

docker-compose up -d

Once it's running, open up localhost:8888 in a browser and there should be some UI showing up
