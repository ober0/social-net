document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.chats-el').forEach(btn => {
        btn.addEventListener('click', function () {
            window.location.href = '/messanger?chat=' + btn.id
        })
    })

    let isInputFocus = false

    let input = document.getElementById('search_chat_input')

    input.addEventListener('focus', function () {
        isInputFocus = true
    })

    input.addEventListener('blur', function () {
        isInputFocus = false
    })

    document.addEventListener('keydown', function (event) {
        if(isInputFocus){
            if(event.key === 'Enter'){
                window.location.href = '/messanger?filter=' + input.value
            }
        }
    })

    document.querySelectorAll('.delete-chat').forEach(btn => {
        btn.addEventListener('click', function (event) {
            event.stopPropagation()
            let chat_id = btn.getAttribute('chat')

            fetch(`/messanger/remove/${chat_id}`, {
                method: 'POST',
            })
                .then(response => response.json())
                .then(data => {
                    if(data.success){
                        btn.parentElement.parentElement.remove()
                    }else {
                        alert(`Ошибка: ${data.error}`)
                    }
                })
        })
    })
})