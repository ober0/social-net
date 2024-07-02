document.getElementById('iconPassword').addEventListener('mousedown', function() {
    const passwordInput = document.getElementById('password');
    passwordInput.type = 'text';
    this.src = this.getAttribute('data-open')
});

document.getElementById('iconPassword').addEventListener('mouseup', function() {
    const passwordInput = document.getElementById('password');
    passwordInput.type = 'password';
    this.src = this.getAttribute('data-hidden')
});

document.getElementById('iconPassword').addEventListener('mouseleave', function() {
    const passwordInput = document.getElementById('password');
    passwordInput.type = 'password';
    this.src = this.getAttribute('data-hidden')
});



document.getElementById('form-main-button').addEventListener('click', function () {
    const _window = document.querySelector('.container');

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const data = {
        email: email,
        password: password
    }

    fetch('/auth', {
        method: 'post',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.result) {
            window.location.href = '/';
        } else {
            document.getElementById('email').value = '';
            document.getElementById('password').value = '';
            _window.style.borderColor = 'pink';
            _window.style.boxShadow = '0 0 20px red';
            document.getElementById('head-h1').innerText = 'Неверный логин или пароль!';
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });


})