document.addEventListener('DOMContentLoaded', function () {
    const OLDTAG = document.getElementById('tag').value;
    document.getElementById('sendDataInfo').addEventListener('click', function () {
        let tag = document.getElementById('tag').value;

        if (tag != OLDTAG) {
            fetch('/groups/tag/check-unique', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tag: tag})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        let name = document.getElementById('name').value;
                        let avatar = document.getElementById('avatar-input').files[0];

                        let formData = new FormData();
                        formData.append('new_tag', tag);
                        formData.append('old_tag', OLDTAG);
                        formData.append('name', name);
                        formData.append('avatar', avatar);

                        sendData(formData);
                    } else {
                        document.getElementById('tag2').style.border = '1px solid red';
                        document.getElementById('tagError').classList.remove('hide');
                        document.getElementById('tagError').innerText = 'Этот тег уже занят';
                    }
                });
        } else {
            let name = document.getElementById('name').value;
            let avatar = document.getElementById('avatar-input').files[0];
            console.log(avatar);

            let formData = new FormData();
            formData.append('new_tag', tag);
            formData.append('old_tag', OLDTAG);
            formData.append('name', name);
            formData.append('avatar', avatar);

            sendData(formData);
        }
    });
});

function sendData(formData) {
    fetch('/groups/update', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let tag = data.tag;
                window.location.href = '/community/' + tag;
            } else {
                let error = document.getElementById('allError');
                error.innerText = data.error;
                error.classList.remove('hide');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
