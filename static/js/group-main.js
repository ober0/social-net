const socketio = io();


function go_edit_prifile(id) {
    window.location.href = '/edit_group?id=' + id;
}

try {
    document.getElementById('goMessage').addEventListener('click', function () {
        window.location.href = '/messanger?chat=' + this.getAttribute('user-tag')
    })
}catch {}

document.getElementById('goFriend').addEventListener('click', function () {
    window.location.href = '/friends?user=' + this.getAttribute('my_tag');
    w
});

document.getElementById('goSubs').addEventListener('click', function () {
    window.location.href = '/groups?user=' + this.getAttribute('my_tag');
});

try {
    document.getElementById('btn-add-friend').addEventListener('click', function () {
        socketio.emit('addFriend_request', {
            friend_id: this.getAttribute('friend_id')
        });
    })
}catch {}

try {
    document.getElementById('btn-remove-friend').addEventListener('click', function () {
        const data = {friend_id: this.getAttribute('friend_id')}
        fetch('friend/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('btn-add-friend').classList.remove('hide');
                    document.getElementById('btn-remove-friend').classList.add('hide');
                } else {
                    console.log(data.error);
                }
            })
    })
}catch {}

try {
    document.getElementById('btn-rem-friend-request').addEventListener('click', function () {
        socketio.emit('removeFriend_request', {
            user_id: this.getAttribute('user_id'),
            friend_id: this.getAttribute('friend_id')
        })
    })
}catch {}

try {
    document.getElementById('btn-add-friend-request').addEventListener('click', function () {
        socketio.emit('addFriend', {
            user_id: this.getAttribute('user_id'),
            friend_id: this.getAttribute('friend_id')
        })
    })
}catch {}

document.getElementById('about-open').addEventListener('click', function (event){
    event.stopPropagation()
    document.getElementById('body').style.opacity = 0.1;
    document.getElementById('about').style.opacity = 1;
    document.getElementById('about').classList.remove('hide');
    document.addEventListener('keydown', hideAboutEsc)

     function handleBodyClick() {
        hideAbout()
        document.getElementById('body').removeEventListener('click', handleBodyClick);
    }

    document.getElementById('body').addEventListener('click', handleBodyClick);
})


function hideAbout() {
    document.getElementById('body').style.opacity = 1;
    document.getElementById('about').classList.add('hide');
    document.removeEventListener('keydown', hideAboutEsc)
}

function hideAboutEsc(event) {
    if (event.key === 'Escape'){
        hideAbout()
    }
}



socketio.on('addFriend_request_result', (data) => {
    if (data.success) {
        document.getElementById('btn-add-friend').classList.add('hide');
        document.getElementById('btn-remove-friend').classList.add('hide');
        document.getElementById('btn-rem-friend-request').classList.remove('hide')
    } else {
        console.log(data.error);
    }
});



socketio.on('removeFriend_request_result', (data) => {
    if (data.success){
        document.getElementById('btn-add-friend').classList.remove('hide');
        document.getElementById('btn-rem-friend-request').classList.add('hide')
        document.getElementById('btn-add-friend-request').classList.add('hide')
    }
    else {
        console.log(data.error)
    }
})

socketio.on('addFriend_result', (data) => {
    if (data.success) {
        document.getElementById('btn-add-friend-request').classList.add('hide')
        document.getElementById('btn-rem-friend-request').classList.add('hide')
        document.getElementById('btn-remove-friend').classList.remove('hide')

    }
})
