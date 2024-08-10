document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('info').addEventListener('input', function() {
        this.style.height = '36px';
        this.style.height = this.scrollHeight + 'px';
    });

    document.getElementById('theme').addEventListener('change', function () {
        let phone = document.getElementById('phone-main')
        if (this.value == 'cooperation' || this.value == 'work'){
            phone.classList.remove('hide')
        }else {
            phone.classList.add('hide')
        }
    })

    document.getElementById('sendDataInfo').addEventListener('click', function () {
        let theme = document.getElementById('theme').value
        let info = document.getElementById('info').value
        let phone = document.getElementById('phone-number').value

        let error = document.getElementById('allError')
        error.classList.add('hide')

        if (info.length < 20 || info.length > 1001){
            error.classList.remove('hide')
            error.innerText = 'Неверная длинна обращения'
            return false
        }
        console.log(info)

        if (theme == 'cooperation' || theme == 'work') {
            if(phone.length <= 3){
                error.classList.remove('hide')
                error.innerText = 'Введите номер телефона'
                return false
            }
        }


        const data = {
            theme: theme,
            info: info,
            phone: phone
        }
        fetch('/support/request/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if(data.success){
                    alert('Обращение отправлено!')
                    window.location.href = '/'
                }
                else {
                    error.classList.remove('hide')
                    error.innerText = data.error
                }
            })
    })
})