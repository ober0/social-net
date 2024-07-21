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


    let isAtBottom = false;

    const urlParams = new URLSearchParams(window.location.search);
    const user_tag = urlParams.get('user');

    window.addEventListener('scroll', function() {
        if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight - 1) {
            if (!isAtBottom) {
                loadMoreFriends();
                isAtBottom = true;
            }
        } else {
            setTimeout(function () {
                isAtBottom = false;
            }, 500)
        }
    });

    function loadMoreFriends() {
        let count = document.querySelectorAll('.friend-body').length

        fetch('friends/load-more', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({count: count, user_tag: user_tag})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    for (let i = 0; i < data.names.length; i++){
                        let friends_data = {
                            name: data.names[i],
                            learn: data.learns[i],
                            avatar_path: data.avatar_paths[i],
                            href: data.hrefs[i],
                            tag: data.tags[i]
                        }
                        createFriendDiv(friends_data)
                    }
                }
            })
    }


    function createFriendDiv(friends_data){
        let name = friends_data.name;
        let learn = friends_data.learn;
        let avatar_path = friends_data.avatar_path;
        let href = friends_data.href;
        let tag = friends_data.tag;

        // Создание элементов
        let friendBody = document.createElement('div');
        friendBody.classList.add('friend-body');

        let friendsContent = document.createElement('div');
        friendsContent.classList.add('friends-content');

        let friendsAvatar = document.createElement('div');
        friendsAvatar.classList.add('friends-avatar');
        let avatarLink = document.createElement('a');
        avatarLink.href = href;
        let avatarImage = document.createElement('img');


        avatarImage.src = `/static/avatars/${avatar_path}`;
        avatarImage.alt = "";
        avatarLink.appendChild(avatarImage);
        friendsAvatar.appendChild(avatarLink);

        let friendsInfo = document.createElement('div');
        friendsInfo.classList.add('friends-info');

        let nameDiv = document.createElement('div');
        nameDiv.classList.add('name');
        let nameBold = document.createElement('b');
        let nameLink = document.createElement('a');
        nameLink.classList.add('friends-name');
        nameLink.href = href;
        nameLink.textContent = name;
        nameBold.appendChild(nameLink);
        nameDiv.appendChild(nameBold);

        friendsInfo.appendChild(nameDiv);

        if (learn) {
            let learnDiv = document.createElement('div');
            learnDiv.classList.add('learn');
            learnDiv.textContent = learn;
            friendsInfo.appendChild(learnDiv);
        }

        let friendsBtn = document.createElement('div');
        friendsBtn.classList.add('friends-btn');

        let sendMessageP = document.createElement('p');
        sendMessageP.setAttribute('tag', tag);
        sendMessageP.id = 'friend-send-message';
        sendMessageP.textContent = 'Написать сообщение';

        let pixelDiv = document.createElement('div');
        pixelDiv.classList.add('pixel');

        let removeFriendP = document.createElement('p');
        removeFriendP.setAttribute('tag', tag);
        removeFriendP.id = 'friend-remove';
        removeFriendP.textContent = 'Удалить из друзей';

        friendsBtn.appendChild(sendMessageP);
        friendsBtn.appendChild(pixelDiv);
        friendsBtn.appendChild(removeFriendP);

        friendsInfo.appendChild(friendsBtn);
        friendsContent.appendChild(friendsAvatar);
        friendsContent.appendChild(friendsInfo);
        friendBody.appendChild(friendsContent);

        let hr = document.createElement('hr');
        friendBody.appendChild(hr);

        document.querySelector('.friends-container').appendChild(friendBody);
    }

})