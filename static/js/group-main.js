const socketio = io();


function go_edit_prifile(id) {
    window.location.href = '/edit_group?id=' + id;
}

try {
    document.getElementById('subscribe').addEventListener('click', function () {
        let btn = this
        const data = {
            tag: btn.getAttribute('group-tag')
        }
        fetch('/group/subscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    btn.classList.add('hide')
                    document.getElementById('unsubscribe').classList.remove('hide')
                    document.getElementById('counter').innerText = Number(document.getElementById('counter').innerText) + 1
                }
                else {
                    window.location.reload()
                }
            })
    })
}catch {}


try {
    document.getElementById('unsubscribe').addEventListener('click', function () {
        let btn = this
        const data = {
            tag: btn.getAttribute('group-tag')
        }
        fetch('/group/unsubscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    btn.classList.add('hide')
                    document.getElementById('subscribe').classList.remove('hide')
                    document.getElementById('counter').innerText = Number(document.getElementById('counter').innerText) - 1
                }
                else {
                    window.location.reload()
                }
            })
    })
}catch {}




