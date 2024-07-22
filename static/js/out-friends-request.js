document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('cancel-request').addEventListener('click', function () {

        let data = {friend_tag: this.getAttribute('tag')}

        fetch('/friend/request/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    this.closest('.friend-body').remove()
                    let req_count = document.querySelectorAll('.friend-body').length
                    if (req_count < 1){
                        document.querySelector('.no-friend').classList.remove('hide')
                    }
                }
            })
    })
})