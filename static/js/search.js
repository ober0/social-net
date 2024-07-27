document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.filter').forEach(btn => {
        btn.addEventListener('click', function () {
            const urlParams = new URLSearchParams(window.location.search);
            const q = urlParams.get('q');

            if (q){
                window.location.href = `/search/${btn.getAttribute('filter-type')}?q=${q}`
            }else {
                window.location.href = `/search/${btn.getAttribute('filter-type')}`
            }
        })
    })

    document.getElementById('search-btn').addEventListener('click',search)

    document.getElementById('search-input').addEventListener('focus', function () {
        document.addEventListener('keydown', keydown)
    })

    document.getElementById('search-input').addEventListener('blur', function () {
        document.removeEventListener('keydown', keydown)
    })

    function keydown(event) {
        if (event.key === 'Enter'){
            search()
        }
    }

    function search() {
        let first_arg = document.querySelector('.active').getAttribute('filter-type')
        let second_arg = document.getElementById('search-input').value


        window.location.href = `/search/${first_arg}?q=${second_arg}`
    }

    let isAtBottom = false;

    window.addEventListener('scroll', function() {
        if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight - 1) {
            if (!isAtBottom) {
                loadMoreContent();
                isAtBottom = true;
            }
        } else {
            setTimeout(function () {
                isAtBottom = false;
            }, 500)
        }
    });

    function loadMoreContent() {
        let el_count = document.querySelectorAll('.content').length
        let first_arg = document.querySelector('.active').getAttribute('filter-type')
        let second_arg = document.getElementById('search-input').value

        let data = {
            count: el_count,
            filter: second_arg
        }
        if (first_arg == 'people'){
            fetch('/search/people/load-more', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success){
                        for (let i = 0; i < result.names.length; i++){
                            let elData = {
                                name: result.names[i],
                                href: result.hrefs[i],
                                avatar: result.avatars[i],
                                city: result.cities[i]
                            }

                            createUser(elData)
                        }
                    }
                })
        }
        else if (first_arg == 'community'){
            fetch('/search/community/load-more', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success){
                        for (let i = 0; i < result.names.length; i++){
                            let elData = {
                                name: result.names[i],
                                href: result.hrefs[i],
                                avatar: result.avatars[i],
                                subscribers: result.subscribers[i]
                            }

                            createGroup(elData)
                        }
                    }
                })
        }

    }
    
    function createUser(elData) {


        let contentDiv = document.createElement('div');
        contentDiv.className = 'content';

        let avatarDiv = document.createElement('div');
        avatarDiv.className = 'el-avatar';

        let link = document.createElement('a');
        link.href = elData.href;

        let img = document.createElement('img');
        img.src = elData.avatar ? `/static/avatars/${elData.avatar}` : '/static/avatars/default.png';
        img.alt = '';

        link.appendChild(img);
        avatarDiv.appendChild(link);

        let infoDiv = document.createElement('div');
        infoDiv.className = 'el-info';

        let nameDiv = document.createElement('div');
        nameDiv.className = 'el-name';

        let nameLink = document.createElement('a');
        nameLink.href = elData.href;
        nameLink.textContent = elData.name;

        nameDiv.appendChild(nameLink);
        infoDiv.appendChild(nameDiv);

        let cityDiv = document.createElement('div');
        cityDiv.className = 'el-city';

        if (elData.city) {
            let cityParagraph = document.createElement('p');
            cityParagraph.textContent = elData.city;
            cityDiv.appendChild(cityParagraph);
        }

        infoDiv.appendChild(cityDiv);
        contentDiv.appendChild(avatarDiv);
        contentDiv.appendChild(infoDiv);
        document.querySelector('.search-result-element').appendChild(contentDiv);

    }
})


function createGroup(elData){
    const subscribersText = elData.subscribers > 0 ? `${elData.subscribers} подписчиков` : `0 подписчиков`;

    const avatar = document.createElement('img');
    avatar.src = elData.avatar || '/static/avatars/default.png';
    avatar.alt = '';

    const avatarLink = document.createElement('a');
    avatarLink.href = elData.href;
    avatarLink.appendChild(avatar);

    const nameLink = document.createElement('a');
    nameLink.href = elData.href;
    nameLink.textContent = elData.name;

    const nameDiv = document.createElement('div');
    nameDiv.className = 'el-name';
    nameDiv.appendChild(nameLink);

    const cityPar = document.createElement('p');
    cityPar.textContent = subscribersText;

    const cityDiv = document.createElement('div');
    cityDiv.className = 'el-city';
    cityDiv.appendChild(cityPar);

    const infoDiv = document.createElement('div');
    infoDiv.className = 'el-info';
    infoDiv.appendChild(nameDiv);
    infoDiv.appendChild(cityDiv);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'content';
    contentDiv.appendChild(avatarLink);
    contentDiv.appendChild(infoDiv);
    document.querySelector('.search-result-element').appendChild(contentDiv);
}