document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('sendDataInfo').addEventListener('click', function () {
        let tag = document.getElementById('tag').value;
        let name = document.getElementById('name').value;

        if (tag.length < 3){
                document.getElementById('tag2').style.border = '1px solid red';
                document.getElementById('tagError').classList.remove('hide');
                document.getElementById('tagError').innerText = 'Тег слишком короткий';
                return false
        }else {
            document.getElementById('tag2').style.border = ''
            document.getElementById('tagError').classList.add('hide');
            document.getElementById('tagError').innerText = '';
        }

        if (!/[a-z0-9]/.test(tag)){
            document.getElementById('tag2').style.border = '1px solid red';
            document.getElementById('tagError').classList.remove('hide');
            document.getElementById('tagError').innerText = 'Тег может состоять из маленьких латинских букв и цифр';
            return false
        }else {
            document.getElementById('tag2').style.border = ''
            document.getElementById('tagError').classList.add('hide');
            document.getElementById('tagError').innerText = '';
        }

        if (/[A-Z]/.test(tag)){
            document.getElementById('tag2').style.border = '1px solid red';
            document.getElementById('tagError').classList.remove('hide');
            document.getElementById('tagError').innerText = 'Тег может состоять из маленьких латинских букв и цифр';
            return false
        }else {
            document.getElementById('tag2').style.border = ''
            document.getElementById('tagError').classList.add('hide');
            document.getElementById('tagError').innerText = '';
        }


        if (name.length < 3){
                document.getElementById('name').style.border = '1px solid red';
                document.getElementById('nameError').classList.remove('hide');
                document.getElementById('nameError').innerText = 'Название слишком короткое';
                return false
        }
        else {
            document.getElementById('name').style.border = ''
            document.getElementById('nameError').classList.add('hide');
            document.getElementById('nameError').innerText = '';
        }

        fetch('/groups/tag/check-unique', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({tag: tag})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    let avatar = document.getElementById('avatar-input').files[0];

                    let formData = new FormData();
                    formData.append('tag', tag);
                    formData.append('name', name);
                    formData.append('avatar', avatar);

                    sendData(formData);
                } else {
                    document.getElementById('tag2').style.border = '1px solid red';
                    document.getElementById('tagError').classList.remove('hide');
                    document.getElementById('tagError').innerText = 'Этот тег уже занят';
                }
            });

    });
});

function sendData(formData) {
    fetch('/new-community/add', {
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
