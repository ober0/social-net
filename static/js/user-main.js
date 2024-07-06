const socketio = io();


function go_edit_prifile() {
    window.location.href = '/edit_user';
}

function go_message() {
    window.location.href = '/messanger';
}

document.getElementById('goFriend').addEventListener('click', function () {
    window.location.href = '/friends?user=' + this.getAttribute('my_tag');
});

document.getElementById('goSubs').addEventListener('click', function () {
    window.location.href = '/subscribe?user=' + this.getAttribute('my_tag');
});

document.getElementById('btn-add-friend').addEventListener('click', function () {
    socketio.emit('addFriend_request', {
        friend_id: this.getAttribute('friend_id')
    });
})

document.getElementById('btn-remove-friend').addEventListener('click', function () {
     socketio.emit('removeFriend', {
        friend_id: this.getAttribute('friend_id')
    });
})

document.getElementById('btn-rem-friend-request').addEventListener('click', function () {
    socketio.emit('removeFriend_request', {
        user_id: this.getAttribute('user_id'),
        friend_id: this.getAttribute('friend_id')
    })
})


document.getElementById('btn-add-friend-request').addEventListener('click', function () {
    socketio.emit('addFriend', {
        user_id: this.getAttribute('user_id'),
        friend_id: this.getAttribute('friend_id')
    })
})


function about() {
    document.getElementById('body').style.opacity = 0.2;
    document.getElementById('about').style.opacity = 1;
    document.getElementById('about').classList.remove('hide');
}

function hideAbout() {
    document.getElementById('body').style.opacity = 1;
    document.getElementById('about').classList.add('hide');
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

socketio.on('removeFriend_result', (data) => {
    if (data.success) {
        document.getElementById('btn-add-friend').classList.remove('hide');
        document.getElementById('btn-remove-friend').classList.add('hide');
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