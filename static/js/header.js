function addNewNotifi(date, from_user, avatar, href, text, type, user_id){
    let notification = {
                href: href,
                from_user_avatar_path: avatar,
                type: type,
                text: text,
                from_user: from_user,
                date: date,
                id: user_id
            }
    const notifDiv = document.createElement('div')
    notifDiv.className = 'notification'
    notifDiv.setAttribute('path', href)

    notifDiv.innerHTML = `
        <div class="notif-main">
            <div class="notif-avatar">
                <div>
                    ${notification.type === 'login-to-account' ? 
                        `<img class="notif-avatar" src="/static/img/${notification.from_user_avatar_path}" alt="">` : 
                        ''
                    }
            
                    ${notification.type === 'newFriendRequest' ? 
                        (notification.from_user_avatar_path ? 
                            `<img class="notif-avatar" src="/static/avatars/users/${notification.from_user_avatar_path}" alt="">` : 
                            `<img class="notif-avatar" src="/static/avatars/default.png" alt="">`
                        ) :
                        ''
                    }
                </div>
            </div>
            <div class="notif-description">
                ${notification.type === 'newFriendRequest' ? 
                    `<p class="notif-text">${notification.text} <a href="${notification.href}">${notification.from_user}</a></p>` : 
                    ''
                }
                
                ${notification.type === 'login-to-account' ? 
                    `<p class="notif-text" style="font-size: 14px !important; color: #a6a6a6 !important;">${notification.text} <a href="${notification.href}">${notification.from_user}</a></p>` : 
                    ''
                }
            </div>
        </div>
        <div class="date" style="display: flex">
            <p class="gray-text">
                ${notification.date}
            </p>
            <div notifi_id="${notification.id}" id="delete-notifi" style="display: flex">
                <img width="20px" height="20px" style="position: relative; top:5px" src="/static/img/trash.png" alt="">
                <p class="gray-text"> Удалить</p>
            </div>
        </div>
    `;


    const hr = document.createElement('hr')
    hr.style.margin = '0';
    hr.style.height = '2px'

    let container = document.getElementById('notification-container')
    let firstChild = container.firstChild;
    container.insertBefore(notifDiv, firstChild)
    container.insertBefore(hr, firstChild)

}


function createUser(avatar, name, second_name, city, tag) {
    const peopleDiv = document.createElement('div')
    peopleDiv.className = 'people'
    peopleDiv.addEventListener('click', function (){
        window.location.href = '/' + tag
    })

    const flexDiv = document.createElement('div')
    flexDiv.style.display = 'flex'

    const avatarDiv = document.createElement('div')
    avatarDiv.className = 'people-avatar'

    const avatarImg = document.createElement('img')
    avatarImg.className = 'avatar-img'
    if (avatar != null){
        avatarImg.src = '/static/avatars/users/' + avatar
    }else {
        avatarImg.src = '/static/avatars/default.png'
    }
    avatarImg.alt = 'Фото пользователя'
    avatarDiv.appendChild(avatarImg)

    const descriptionDiv = document.createElement('div')
    descriptionDiv.className = 'people-description'

    const nameDiv = document.createElement('div')
    nameDiv.className = 'people-name'

    const nameContent = document.createElement('div')
    nameContent.textContent = name + " " + second_name
    nameDiv.appendChild(nameContent)
    descriptionDiv.appendChild(nameDiv)

    const cityDiv = document.createElement('div')
    cityDiv.className = 'people-city'

    const cityContent = document.createElement('div')
    cityContent.textContent = city
    cityDiv.appendChild(cityContent)
    descriptionDiv.appendChild(cityDiv)

    flexDiv.appendChild(avatarDiv)
    flexDiv.appendChild(descriptionDiv)

    peopleDiv.appendChild(flexDiv)

    document.getElementById('people-container').appendChild(peopleDiv)
}

function createGroup(avatar, name, subscribers, tag){
    const groupDiv = document.createElement('div')
    groupDiv.className = 'group'
    groupDiv.addEventListener('click', function (){
        window.location.href = '/community/' + tag
    })

    const flexDiv = document.createElement('div')
    flexDiv.style.display = 'flex'

    const avatarDiv = document.createElement('div')
    avatarDiv.className = 'group-avatar'

    const avatarImg = document.createElement('img')
    avatarImg.className = 'avatar-img'
    if (avatar != null){
        avatarImg.src = '/static/avatars/groups/' + avatar
    }else {
        avatarImg.src = '/static/avatars/default.png'
    }
    avatarImg.alt = 'Фото сообщества'
    avatarDiv.appendChild(avatarImg)

    const descriptionDiv = document.createElement('div')
    descriptionDiv.className = 'group-description'

    const nameDiv = document.createElement('div')
    nameDiv.className = 'group-name'

    const nameContent = document.createElement('div')
    nameContent.textContent = name
    nameDiv.appendChild(nameContent)
    descriptionDiv.appendChild(nameDiv)

    const cityDiv = document.createElement('div')
    cityDiv.className = 'group-subscribers'

    const cityContent = document.createElement('div')
    cityContent.textContent = subscribers + ' подписчиков'
    cityDiv.appendChild(cityContent)
    descriptionDiv.appendChild(cityDiv)

    flexDiv.appendChild(avatarDiv)
    flexDiv.appendChild(descriptionDiv)

    groupDiv.appendChild(flexDiv)

    document.getElementById('group-container').appendChild(groupDiv)
}

function hideSearch(){
    document.getElementById('search_result').classList.add('hide')
    document.getElementById('body').removeEventListener('click', hideSearch)
     document.removeEventListener('keydown', hideSearchEsc)
}

function hideSearchEsc(event) {
    if (event.key === 'Escape'){
        hideSearch()
    }
}





function openNotification(event){

    fetch('/notificationView', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(data => {
            if (data.success){
                document.getElementById('badge').classList.add('hide')
                document.getElementById('notifi-counter').innerText = 0
            }

        })


    document.getElementById('notifications').classList.remove('hide')
    event.stopPropagation()

    document.getElementById('notifications').addEventListener('click', function (event) {
        event.stopPropagation()
    })
    function closeNotifiEsc(event) {
        if (event.key === 'Escape'){
            closeNotifi()
        }
    }

    function closeNotifi(){
        document.removeEventListener('keydown', closeNotifiEsc)
        document.getElementById('notifications').classList.add('hide')
        document.getElementById('open-notifi').addEventListener('click', openNotification)
    }
    document.getElementById('body').addEventListener('click', closeNotifi)
    document.addEventListener('keydown', closeNotifiEsc)


}

document.addEventListener('DOMContentLoaded', function () {
    let searchInput = document.getElementById('search-main')

    const soc = io()

    soc.emit('join_main_room', {})

    soc.on('newNotification', (data) => {
        document.getElementById('badge').classList.remove('hide')
        document.getElementById('notifi-counter').innerText = Number(document.getElementById('notifi-counter').innerText) + 1
        document.getElementById('no-notifi-p').classList.add('hide')
        console.log(data)
        addNewNotifi(data.date, data.from_user, data.from_user_avatar_path, data.href, data.text, data.type, data.user_id)
    })


    document.getElementById('user-right-menu').addEventListener('click', function () {

    })

    document.getElementById('btn-setting').addEventListener('click', function () {
        window.location.href = '/setting'
    })

    document.getElementById('btn-support').addEventListener('click', function () {
        window.location.href = '/support'
    })

    document.getElementById('btn-exit').addEventListener('click', function () {
        window.location.href = '/exit'
    })



    searchInput.addEventListener('input', function () {
        let searchValue = searchInput.value;

        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ data: searchValue })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success){
                let users = data.users
                let groups = data.groups

                let peoples = document.querySelectorAll('.people')
                peoples.forEach(el => {
                    el.remove()
                })

                let groups_ = document.querySelectorAll('.group')
                groups_.forEach(el => {
                    el.remove()
                })

                if (users.names.length == 0){
                    document.getElementById('people-h').style.display = 'none'
                }else {
                    document.getElementById('people-h').style.display = 'block'
                }

                if (groups.names.length == 0){
                    document.getElementById('group-h').style.display = 'none'
                }else {
                    document.getElementById('group-h').style.display = 'block'
                }

                document.getElementById('search_result').classList.remove('hide')
                document.getElementById('all-result').classList.remove('hide')
                document.getElementById('no-info').classList.add('hide')
                for (let i = 0; i < 3 && i < users.names.length; i++){
                    let avatar = users.avatar_paths[i]
                    let city = users.city[i]
                    let name = users.names[i]
                    let second_name = users.second_names[i]
                    let tag = users.user_tags[i]
                    createUser(avatar, name, second_name, city, tag)
                }

                for (let i = 0; i < 3 && i < groups.names.length; i++){
                    let avatar = groups.avatar_paths[i]
                    let subscribers = groups.subscribers[i]
                    let name = groups.names[i]
                    let tag = groups.tags[i]

                    createGroup(avatar, name, subscribers, tag)
                }

                document.getElementById('search_result').addEventListener('click', function (event) {
                    event.stopPropagation()
                })

                document.getElementById('body').addEventListener('click', hideSearch)
                document.addEventListener('keydown', hideSearchEsc)

                if (groups.names.length == 0 && users.names.length == 0){
                    document.getElementById('all-result').classList.add('hide')
                    document.getElementById('no-info').classList.remove('hide')
                }
            }
        })
    })

    document.querySelectorAll('.notification').forEach(notif => {
        notif.addEventListener('click', function (){
            window.location.href = this.getAttribute('path')
        })
    })

    document.getElementById('open-notifi').addEventListener('click', openNotification)

    document.getElementById('notifi-delete-all-div').addEventListener('click', function (){
        fetch('/notificationDelete', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({notifi: 'all'})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    let parentEl = document.getElementById('notification-container')
                    while (parentEl.firstChild) {
                        parentEl.removeChild(parentEl.firstChild);
                    }
                    document.getElementById('notifications').classList.add('hide')
                    document.getElementById('open-notifi').addEventListener('click', openNotification)
                    document.getElementById('no-notifi-p').classList.remove('hide')
                }

            })
    })

    document.getElementById('delete-notifi').addEventListener('click', function (event){
        event.stopPropagation()
        let not_id = this.getAttribute('notifi_id')
        this.parentElement.parentElement.remove()
        fetch('/notificationDelete', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({notifi: not_id})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){

                }
            })
    })
    



})

