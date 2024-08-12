document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.btn-change-theme').forEach(btn => {
        btn.addEventListener('click', function () {
            window.location.href = 'support?q=' + btn.id
        })
    })

    document.querySelector('.goMessanger').addEventListener('click', function () {
        window.location.href = '../messanger?chat=' + this.getAttribute('tag')
    })

    document.querySelectorAll('.notification-send').forEach(btn => {
        btn.addEventListener('click', function () {
            let tag = this.getAttribute('tag')
            let text = document.querySelector('.notifi-message-' + tag)

            fetch('/notification/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({text:text.value, tag:tag})
            })
                .then(response => response.json())
                .then(data => {
                    if(data.success){
                        text.value = ''
                        alert('Отправлено')
                    }
                    else {
                        alert('Ошибка', data.error)
                    }
                })
        })
    })

    let counter = document.getElementById('req-counter')
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', function () {
            let requestId = this.getAttribute('request-id')

            fetch('/admin/support/request/remove', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({id:requestId})
            })
                .then(response => response.json())
                .then(data => {
                    if(data.success){
                        this.parentElement.parentElement.remove()
                        counter.innerText = Number(counter.innerText) - 1
                    }
                    else {
                        alert('Ошибка', data.error)
                    }
                })
        })
    })
})