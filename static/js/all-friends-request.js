document.addEventListener('DOMContentLoaded', function (){
    document.getElementById('approve-request').addEventListener('click', function () {
        let data = {user_tag: this.getAttribute('tag')}
        fetch('/friend/add', {
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
                    let req_counter = document.getElementById('all_req_counter')
                    req_counter.innerText = Number(req_counter.innerText) - 1
                    if (Number(req_counter.innerText) < 1){
                        req_counter.parentElement.classList.add('hide')
                        document.querySelector('.no-friend').classList.remove('hide')
                    }
                }
            })
    })

    document.getElementById('reject-request').addEventListener('click', function () {
        let data = {user_tag: this.getAttribute('tag')}
        console.log(data)
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
                    let req_counter = document.getElementById('all_req_counter')
                    req_counter.innerText = Number(req_counter.innerText) - 1

                    let req_counter_left = document.getElementById('all_req_counter-left-menu')
                    req_counter_left.innerText = Number(req_counter_left.innerText) - 1

                    if (Number(req_counter.innerText) < 1){
                        req_counter.parentElement.classList.add('hide')
                        req_counter_left.parentElement.classList.add('hide')
                        document.querySelector('.no-friend').classList.remove('hide')
                    }
                }
            })
    })
})