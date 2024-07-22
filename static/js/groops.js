document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.request-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            fetch('groups/unsubscribe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({tag: this.getAttribute('tag')})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.closest('.friend-body').remove()
                    document.querySelector('.friends-counter').innerText = `Всего подписок: ${Number(document.querySelector('.friends-counter').innerText.split(': ')[1]) - 1}`
                    if (document.querySelector('.friends-counter').innerText.split(': ')[1] == '0'){
                        document.querySelector('.no-friend').classList.remove('hide')
                    }
                } else {
                    console.log(data.error);
                }
            })
        })
    })

})