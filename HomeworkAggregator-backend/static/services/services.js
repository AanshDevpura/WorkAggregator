//TODO
function addCredentials(ed_platform_form, token, userName) {
    const credentials = {
        platform: ed_platform_form,
        userid: userName,
        credentials: {
            username: null,
            password: null,
            accesstoken: token, 
        }
    };

    console.log(credentials);

    fetch('/api/v1/addcredentials', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', 
        },
        body: JSON.stringify(credentials)
      })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error('Error:', error)); 
}

function postCredentials(ed_platform_form) {
    var form = document.getElementById(ed_platform_form);
    var formData = new FormData(form);

    // Access the 'user' attribute from the form
    var userName = form.getAttribute('user');

    var formData = new FormData(form);
    var tokenKey = formData.get('tokenKey');

    console.log(tokenKey);
    console.log(userName);

    addCredentials(ed_platform_form, tokenKey, userName);
}

function generateSchedule(userid) {
    const userid_body = {
            userid: userid
    }
    fetch('/api/v1/generateschedule/' + userid, {
        method: 'GET'
      })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error('Error:', error)); 


    return null;
}


document.getElementById('canvasForm').addEventListener('submit', function(event) {
    event.preventDefault(); // This stops the form from submitting the traditional way.
    postCredentials('canvasForm');
});

document.getElementById('moodleForm').addEventListener('submit', function(event) {
    event.preventDefault(); // This stops the form from submitting the traditional way.
    postCredentials('moodleForm');
});

document.getElementById('prairielearnForm').addEventListener('submit', function(event) {
    event.preventDefault(); // This stops the form from submitting the traditional way.
    postCredentials('prairielearnForm');
});

document.getElementById('gradescopeForm').addEventListener('click', function(event) { 
    event.preventDefault(); // This stops the form from submitting the traditional way.
    postCredentials('gradescopeForm');
});

document.getElementById('generateScheduleButton').addEventListener('click', function(event) { 
    const userName = document.getElementById('generateScheduleButton').getAttribute('user');
    generateSchedule(userName);
});

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