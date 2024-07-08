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

document.addEventListener('DOMContentLoaded', function () {
    let searchInput = document.getElementById('search-main')

    const soc = io()

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
})