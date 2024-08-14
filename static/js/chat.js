document.addEventListener('DOMContentLoaded', function (){
    function createMessage(messageData, scroll) {

        const messageEl = document.createElement('div');
        messageEl.classList.add('message-el');

        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');

        const avatarLink = document.createElement('a');
        avatarLink.href = `/${messageData.tag}`;

        const avatarImg = document.createElement('img');
        avatarImg.classList.add('avatar-img');
        avatarImg.src = messageData.avatar ? `static/avatars/users/${messageData.avatar}` : `static/avatars/default.png`;
        avatarImg.alt = '';
        avatarLink.appendChild(avatarImg);
        avatarDiv.appendChild(avatarLink);

        const otherDiv = document.createElement('div');
        otherDiv.classList.add('other');

        const nameDiv = document.createElement('div');
        nameDiv.classList.add('name');

        const nameLink = document.createElement('a');
        nameLink.href = `/${messageData.tag}`;
        nameLink.textContent = messageData.name;
        nameDiv.appendChild(nameLink);

        const timeP = document.createElement('p');
        timeP.style.color = '#656565';
        timeP.style.fontSize = '14px';
        timeP.style.position = 'relative';
        timeP.style.top = '2px';
        timeP.textContent = messageData.time;
        nameDiv.appendChild(timeP);

        otherDiv.appendChild(nameDiv);

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        if (messageData.self) {
            messageDiv.classList.add('blue');
        }
        messageDiv.textContent = messageData.message;

        otherDiv.appendChild(messageDiv);

        messageEl.appendChild(avatarDiv);
        messageEl.appendChild(otherDiv);


        document.querySelector('.message-container').appendChild(messageEl)
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