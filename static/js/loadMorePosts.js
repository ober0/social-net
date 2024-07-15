function likePost(id, likes_div) {
    let data = {id: id}
    fetch('likePost', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({id: id})
    })
        .then(response => response.json())
        .then(data => {
            if (data.success){
                likes_div.querySelector('.like-image').style.animation = '';
                if (data.liked){
                    let counter = likes_div.querySelector('#like-counter')
                    counter.innerText = Number(counter.innerText) + 1
                    counter.style.color = 'red'

                    let image = likes_div.querySelector('.like-image')
                    image.src = '/static/img/like_1.png'
                    image.style.animation = 'fade-in 0.5s ease-in-out';

                }
                else {
                    let counter = likes_div.querySelector('#like-counter')
                    counter.innerText = Number(counter.innerText) - 1
                    counter.style.color = 'white'

                    let image = likes_div.querySelector('.like-image')
                    image.src = '/static/img/like_0.png'
                    image.style.animation = 'fade-out 0.5s ease-in-out';

                }

            }
        })
}


function remPost(post_id){


    fetch('removePost', {
        method : "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({id: post_id})
    })
        .then(response => response.json())
        .then(data => {
            if (data.success){
                let posts = document.querySelectorAll('.post-rem')
                posts.forEach(post => {
                    if (post.getAttribute('post-id') == post_id){
                        post.parentElement.parentElement.remove()
                        loadMoreContent(1);
                    }
                })
            }

        })
}


function createPost(postData) {
    let postDiv = document.createElement('div');
    postDiv.classList.add('post');
    postDiv.style.marginTop = '25px';

    let headerDiv = document.createElement('div');
    headerDiv.classList.add('post-header');

    let avatarDiv = document.createElement('div');
    avatarDiv.classList.add('post-avatar');
    let avatarImg = document.createElement('img');
    avatarImg.src = `/static/avatars/${postData.avatar}`;
    avatarImg.alt = '';
    avatarDiv.appendChild(avatarImg);
    headerDiv.appendChild(avatarDiv);

    let infoDiv = document.createElement('div');
    infoDiv.classList.add('post-info');

    let authorDiv = document.createElement('div');
    authorDiv.classList.add('post-author');
    let authorLink = document.createElement('a');
    authorLink.href = `/${postData.href}`;
    authorLink.style.marginBottom = '0';
    authorLink.textContent = postData.username;
    authorDiv.appendChild(authorLink);
    infoDiv.appendChild(authorDiv);

    let dateDiv = document.createElement('div');
    dateDiv.classList.add('post-date');
    let dateP = document.createElement('p');
    dateP.style.color = '#a6a6a6';
    dateP.style.fontSize = '14px';
    dateP.textContent = postData.date;
    dateDiv.appendChild(dateP);
    infoDiv.appendChild(dateDiv);

    headerDiv.appendChild(infoDiv);

    if (postData.self == 1) {
        let pRemove = document.createElement('p')
        pRemove.classList.add('post-rem')
        pRemove.innerText = 'Удалить пост'
        pRemove.setAttribute('post-id', postData.id)
        pRemove.addEventListener('click', function () {
            remPost(postData.id)
        })

        headerDiv.appendChild(pRemove)
    }

    postDiv.appendChild(headerDiv);


    let contentDiv = document.createElement('div');
    contentDiv.classList.add('post-content');

    if (postData.text) {
        let textDiv = document.createElement('div');
        textDiv.classList.add('post-text');
        textDiv.textContent = postData.text;
        textDiv.style.marginTop = '15px'
        contentDiv.appendChild(textDiv);
    }



    if (postData.files) {
        let filesDiv = document.createElement('div');
        filesDiv.classList.add(`post-files`);
        filesDiv.classList.add('file-' + postData.files.length)
        postData.files.forEach(file => {
            let fileDiv = document.createElement('div');
            fileDiv.classList.add('post-file');

            let fileType = file.split('.').pop().toLowerCase();
            if (fileType === 'mp4') {
                let videoEl = document.createElement('video');
                videoEl.classList.add('post-file-el');
                videoEl.controls = true;
                let sourceEl = document.createElement('source');
                sourceEl.src = `/static/users/video/${file}`;
                sourceEl.type = 'video/mp4';
                videoEl.appendChild(sourceEl);
                fileDiv.appendChild(videoEl);
            } else {
                let imgEl = document.createElement('img');
                imgEl.classList.add('post-file-el');
                imgEl.src = `/static/users/photos/${file}`;
                imgEl.alt = '';
                fileDiv.appendChild(imgEl);
            }

            filesDiv.appendChild(fileDiv);
        })
        contentDiv.appendChild(filesDiv);

    }
    postDiv.appendChild(contentDiv);

    let actionsDiv = document.createElement('div');
    actionsDiv.style.display = 'flex';
    if (!postData.files) {
        actionsDiv.style.marginTop = '10px'
    }
    let likesDiv = document.createElement('div');
    likesDiv.id = 'likes';
    likesDiv.addEventListener('click', function () {
        likePost(postData.id, likesDiv)
    })
    let likeImg = document.createElement('img');
    likeImg.classList.add('like-image');
    likeImg.src = `/static/img/like_${postData.liked == 1 ? 1 : 0}.png`;
    likeImg.alt = '';
    likesDiv.appendChild(likeImg);
    let likeCounterP = document.createElement('p');
    likeCounterP.id = 'like-counter';
    likeCounterP.textContent = postData.likes;
    likeCounterP.style.color = `${postData.liked == 1 ? 'red' : 'white'}`
    likesDiv.appendChild(likeCounterP);
    actionsDiv.appendChild(likesDiv);

    let commentsDiv = document.createElement('div');
    commentsDiv.id = 'comments';
    let commentImg = document.createElement('img');
    commentImg.classList.add('comment-image');
    commentImg.src = '/static/img/comment.png';
    commentImg.alt = '';
    commentsDiv.appendChild(commentImg);
    let commentCounterP = document.createElement('p');
    commentCounterP.id = 'comment-counter';
    commentCounterP.textContent = postData.comments;
    commentsDiv.appendChild(commentCounterP);
    actionsDiv.appendChild(commentsDiv);

    postDiv.appendChild(actionsDiv);


    document.getElementById('posts-container').appendChild(postDiv);
}


document.addEventListener('DOMContentLoaded', function () {
    loadMoreContent(10)
    let remPostButtons = document.querySelectorAll('.post-rem')
    remPostButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            remPost(btn.getAttribute('post-id'))
        })
    })
})



let isAtBottom = false;

window.addEventListener('scroll', function() {
    if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight - 1) {
        if (!isAtBottom) {
            loadMoreContent(5);
            isAtBottom = true;
        }
    } else {
        isAtBottom = false;
    }
});

function loadMoreContent(count) {
    let all = false
    let tag = null
    if (window.location.pathname == '/'){
        all = true
    }
    else {
        tag = window.location.pathname.split('/')[1]
    }
    let postNext = document.querySelectorAll('.post').length
    fetch('/loadMorePosts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({startWith: postNext, all: all, count: count, tag:tag})
    })
        .then(response => response.json())
        .then(data => {
            if (data.success){
                for (let i = 0; i < data.usernames.length; i++){
                    let postData = {
                        username: data.usernames[i],
                        avatar: data.avatars[i],
                        text: data.text[i],
                        files: data.files[i],
                        date: data.dates[i],
                        likes: data.likes[i],
                        comments: data.comments[i],
                        href: data.href[i],
                        self: data.selfs[i],
                        id: data.ids[i],
                        liked: data.liked[i]
                    }
                    createPost(postData)
                }
            }
        })
}