document.getElementById('canvasForm').addEventListener('submit', function(event) {
    event.preventDefault(); // This stops the form from submitting the traditional way.
    requestData();
});

document.getElementById('moodleForm').addEventListener('submit', function(event) {
    event.preventDefault(); // This stops the form from submitting the traditional way.
    requestData();
});

document.getElementById('prairielearnForm').addEventListener('submit', function(event) {
    event.preventDefault(); // This stops the form from submitting the traditional way.
    requestData();
});

//TODO
function addCredentials(userid, credentials) {
    return null;
}

//TODO
function generateSchedule(userid) {
    return null;
}

//TODO
function modifySchedule(userid, newschedule) {
    return null;
}

function requestData() {
    fetch('/api/assignments')
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
        .catch(error => console.error('Error:', error));
}
function createData() {
    var data = "hi";
    fetch('/api/assignments', {
        method: 'POST', // Specify the method
        headers: {'Content-Type': 'application/json', // Specify the content type
    },
    body: JSON.stringify(data), // Convert the JavaScript object to a JSON string
    })
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function deleteData() {
    fetch('/api/assignments/12', {
        method: 'DELETE', // Specify the method
        headers: {'Content-Type': 'application/json', // Specify the content type
},
    body: JSON.stringify(data), // Convert the JavaScript object to a JSON string
    })
    .then(response => response.json()) // Parse the JSON response
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
        
}