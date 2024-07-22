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


    let isAtBottom = false;

    const urlParams = new URLSearchParams(window.location.search);
    const user_tag = urlParams.get('user');

    window.addEventListener('scroll', function() {
        if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight - 1) {
            if (!isAtBottom) {
                console.log(1)
                loadMoreGroups();
                isAtBottom = true;
            }
        } else {
            setTimeout(function () {
                isAtBottom = false;
            }, 500)
        }
    });

    function loadMoreGroups() {
        let count = document.querySelectorAll('.friend-body').length

        fetch('groups/load-more', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({count: count, user_tag: user_tag})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    console.log(2)
                    for (let i = 0; i < data.title.length; i++){
                        let group_data = {
                            name: data.title[i],
                            subscribers: data.subs[i],
                            avatar_path: data.avatar_paths[i],
                            href: data.hrefs[i],
                            tag: data.tags[i],
                            self: data.self
                        }
                        createGroupDiv(group_data)
                    }
                }
                else {
                    console.log('error')
                }
            })
    }

    function createGroupDiv(group_data) {
        let div = document.createElement('div');
        div.className = 'friend-body';

        let contentDiv = document.createElement('div');
        contentDiv.className = 'friends-content';

        let avatarDiv = document.createElement('div');
        avatarDiv.className = 'friends-avatar';

        let avatarLink = document.createElement('a');
        avatarLink.href = group_data.href;

        let avatarImg = document.createElement('img');
        avatarImg.src = `/static/avatars/${group_data.avatar_path}`;
        avatarImg.alt = '';

        avatarLink.appendChild(avatarImg);
        avatarDiv.appendChild(avatarLink);

        let infoDiv = document.createElement('div');
        infoDiv.className = 'friends-info';

        let nameDiv = document.createElement('div');
        nameDiv.className = 'name';

        let nameBold = document.createElement('b');

        let nameLink = document.createElement('a');
        nameLink.className = 'friends-name';
        nameLink.href = group_data.href;
        nameLink.textContent = group_data.name;

        nameBold.appendChild(nameLink);
        nameDiv.appendChild(nameBold);

        let learnDiv = document.createElement('div');
        learnDiv.className = 'learn';
        learnDiv.textContent = `Подписчиков: ${group_data.subscribers}`;

        infoDiv.appendChild(nameDiv);
        infoDiv.appendChild(learnDiv);
        if (group_data.self) {
            let requestBtn = document.createElement('div');
            requestBtn.className = 'request-btn';
            requestBtn.style.cursor = 'pointer';
            requestBtn.setAttribute('tag', group_data.tag);
            requestBtn.textContent = 'Отписаться';
            requestBtn.addEventListener('click', function () {
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
            infoDiv.appendChild(requestBtn);
        }

        contentDiv.appendChild(avatarDiv);
        contentDiv.appendChild(infoDiv);

        div.appendChild(contentDiv);

        let hr = document.createElement('hr');
        div.appendChild(hr);

        document.querySelector('.friends-container').appendChild(div);
    }



    document.getElementById('friends-input').addEventListener('input', function () {
        document.querySelector('.img-load').classList.remove('hide')
        let filter = this.value
        if (filter == ''){
            document.querySelector('.no-friend').classList.add('hide')
            loadMoreFriends()
            document.querySelector('.img-load').classList.add('hide')
        }
        else {
            setTimeout(function () {
                fetch('groups/load-more?filter=' + filter, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({user_tag: user_tag})
                })
                    .then(response => response.json())
                    .then(data => {
                        document.querySelectorAll('.friend-body').forEach(friend => {
                            friend.remove()
                        })
                        document.querySelector('.img-load').classList.add('hide')
                        if (data.success){
                            if (data.title.length > 0) {
                                document.querySelector('.no-friend').classList.add('hide')
                                for (let i = 0; i < data.title.length; i++) {
                                    let group_data = {
                                        name: data.title[i],
                                        subscribers: data.subs[i],
                                        avatar_path: data.avatar_paths[i],
                                        href: data.hrefs[i],
                                        tag: data.tags[i],
                                        self: data.self
                                    }

                                    createGroupDiv(group_data)
                                }
                            }
                            else {
                                document.querySelector('.no-friend').classList.remove('hide')
                            }
                        }
                    })
            },200)

        }
    })

})