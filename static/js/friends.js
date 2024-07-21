document.addEventListener('DOMContentLoaded', function (){
    document.getElementById('friend-send-message').addEventListener('click', function (){
        window.location.href = 'chats/' + this.getAttribute('tag')
    })

    document.getElementById('friend-remove').addEventListener('click', function () {
        fetch('friend/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({friend_tag: this.getAttribute('tag')})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.closest('.friend-body').remove()
                    document.querySelector('.friends-counter').innerText = `Всего друзей: ${Number(document.querySelector('.friends-counter').innerText.split(': ')[1]) - 1}`
                    if (document.querySelector('.friends-counter').innerText.split(': ')[1] == '0'){
                        document.querySelector('.no-friend').classList.remove('hide')
                    }
                } else {
                    console.log(data.error);
                }
            })
    })
})