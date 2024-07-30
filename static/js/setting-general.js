document.addEventListener('DOMContentLoaded', function (){
    const access_page = document.getElementById('access-page')
    const body = document.getElementById('body')
    let unsuccessful = 0
    document.getElementById('tag').addEventListener('click', function () {
        window.location.href = '/edit_user#tag'
    })
        
    document.getElementById('email').addEventListener('click', function () {
        window.location.href = '/support?q=change_email'
    })
    
    document.getElementById('password').addEventListener('click', function () {

        access_page.classList.remove('hide')
        body.style.opacity = 0.1

    })

    document.getElementById('cancel-auth').addEventListener('click', function () {
        access_page.classList.add('hide')
        body.style.opacity = 1
        document.getElementById('password-input').value = ''
    })

    document.getElementById('auth').addEventListener('click', function () {
        let password = document.getElementById('password-input').value
        let data = {password: password}
        console.log(data)
        fetch('/check-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    access_page.classList.add('hide')
                    let newPassword_input = document.createElement('div')
                    newPassword_input.id = 'newPassDiv'
                    newPassword_input.innerHTML = `
                        <div class="content">
                            <input type="hidden" name="" id='secret_key' value="${data.secret_key}">
                            <div class="header">
                                <h3>Введите новый пароль:</h3>
                            </div>
                            <div class="input-password">
                                <input type="password" id="password-new" class="form-control">
                                <p style="color:red" id="password-error"></p>
                            </div>
                            <div class="buttons">
                                <input type="button" value="Отмена" id="cancel-auth-new">
                                <input type="button" value="Войти" id="auth-new">
                            </div>
                        </div>
                    `
                    document.body.appendChild(newPassword_input)

                    document.getElementById('cancel-auth-new').addEventListener('click', function () {
                        access_page.classList.add('hide')
                        document.getElementById('newPassDiv').remove()
                        body.style.opacity = 1
                        document.getElementById('password-input').value = ''
                    })



                    document.getElementById('auth-new').addEventListener('click', function () {
                        let password = document.getElementById('password-new').value
                        let error = ''
                        if (password.length < 8) {
                            error = 'Пароль должен быть минимум из 8 символов'
                        }
                        if (!/[a-zA-Z]/.test(password)){
                            error = 'В пароле должна быть минимум 1 буква'
                        }
                        if (!/\d/.test(password)){
                            error = 'В пароле должна быть минимум 1 цифра'
                        }
                        if (/[а-яА-Я]/.test(password)) {
                            error = 'Пароль может содержать буквы только латинского алфавита'
                        }
                        if (error == '') {
                            let data = {password: password, secret_key: document.getElementById('secret_key').value}
                            fetch('/new-password', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify(data)
                            })
                                .then(response => response.json())
                                .then(data => {
                                    if (data.success) {
                                        access_page.classList.add('hide')
                                        document.getElementById('newPassDiv').remove()
                                        body.style.opacity = 1
                                    } else {
                                        if (data.error == 'code_injection') {
                                            window.location.href = '/exit'
                                        } else {
                                            alert('Произошла ошибка')
                                            access_page.classList.add('hide')
                                            document.getElementById('newPassDiv').remove()
                                            body.style.opacity = 1
                                        }
                                    }
                                })
                        }else {
                            document.getElementById('password-input').style.border = '1px solid red'
                            document.getElementById('password-input').value = ''
                            document.getElementById('password-error').innerText = error
                        }
                    })

                }
                else {
                    document.getElementById('password-input').style.border = '1px solid red'
                    document.getElementById('password-input').value = ''
                    unsuccessful++
                    if (unsuccessful > 2){
                        window.location.href = '/exit'
                    }
                }
            })
    })
})