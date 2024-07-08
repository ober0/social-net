function createUser(avatar, name, second_name, city) {


    const peopleDiv = document.createElement('div')
    peopleDiv.className = 'people'

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

                let peoples = document.querySelectorAll('.people')
                peoples.forEach(el => {
                    el.remove()
                })
                if (users.names.length == 0){
                    document.getElementById('people-h').style.display = 'none'
                }else {
                    document.getElementById('people-h').style.display = 'block'
                }
                document.getElementById('search_result').classList.remove('hide')

                for (let i = 0; i < 3 && i < users.names.length; i++){
                    let avatar = users.avatar_paths[i]
                    let city = users.city[i]
                    let name = users.names[i]
                    let second_name = users.second_names[i]

                    createUser(avatar, name, second_name, city)
                }
            }
        })
    })
})