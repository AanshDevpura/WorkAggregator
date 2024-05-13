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
    var tokenKey = ed_platform_form == 'canvasForm' || ed_platform_form == 'moodleForm' ? formData.get('tokenKey') : `${formData.get('tokenUser')},${formData.get('tokenPass')}`;

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

window.addEventListener('DOMContentLoaded', (event) => {

    const canvasForm = document.getElementById('canvasForm');

    if (canvasForm) {
        document.getElementById('canvasForm').addEventListener('submit', function(event) {
            event.preventDefault(); // This stops the form from submitting the traditional way.
            postCredentials('canvasForm');
        });
        
        document.getElementById('moodleForm').addEventListener('submit', function(event) {
            event.preventDefault(); // This stops the form from submitting the traditional way.
            postCredentials('moodleForm');
        });
        
        document.getElementById('gradescopeForm').addEventListener('click', function(event) { 
            event.preventDefault(); // This stops the form from submitting the traditional way.
            postCredentials('gradescopeForm');
        });
    }
});