document.addEventListener('DOMContentLoaded', function (){
    function createMessage(data, scroll) {

        // Тут код добавления сообщения

        if(scroll){
            scrollbar.scrollTop = scrollbar.scrollHeight
        }
    }


    let scrollbar = document.querySelector('.message-container')
    scrollbar.scrollTop = scrollbar.scrollHeight

     document.addEventListener('keydown', function (event){
        if(event.key === 'Escape'){
             window.location.href = '/messanger'
        }
    })

    document.querySelector('.chat-back').addEventListener('click', function (){
        window.location.href = '/messanger'
    })

    let isMessageInputActive = false

    document.getElementById('message-input').addEventListener('focus', function () {
        isMessageInputActive = true
    })

    document.getElementById('message-input').addEventListener('blur', function () {
        isMessageInputActive = false
    })

    document.addEventListener('keydown', function (event){
        if(event.key === 'Enter'){
            if(isMessageInputActive){
                let message = document.getElementById('message-input').value
                if(message.length > 0) {
                    document.getElementById('message-input').value = ''
                    const urlParams = new URLSearchParams(window.location.search);
                    const chat = urlParams.get('chat');
                    let data = {
                        message: message,
                        chat: chat
                    }
                    fetch('/message/new', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                        .then(response => response.json())
                        .then(data => {
                            if(data.success){
                                let messageData = {
                                    avatar: data.avatar,
                                    name: data.name,
                                    time: data.time,
                                    message: data.message,
                                    self: true
                                }
                                let scroll = scrollbar.scrollTop + scrollbar.clientHeight === scrollbar.scrollHeight
                                createMessage(data, scroll)
                            }
                        })
                }
            }
        }
    })

    let socket = io()
    socket.emit('join_main_room', {});

    socket.on('newMessage', (data) => {
        if(data.success){
            let messageData = {
                avatar: data.avatar,
                name: data.name,
                time: data.time,
                message: data.message,
                self: data.self
            }
            let scroll = scrollbar.scrollTop + scrollbar.clientHeight === scrollbar.scrollHeight
            createMessage(data, scroll)
        }
    })
})