function sendComment(comment,commentsContainerDiv, commentCounterP, post_id) {
    if (commentsContainerDiv.parentElement.parentElement.querySelector('#comment-input').value.length > 0) {
        fetch('comments/add', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({comment: comment, post_id: post_id})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    let commentsData = {
                        usernames: data.usernames,
                        usernames: data.usernames,
                        avatars: data.avatars,
                        texts: data.texts,
                        times: data.times,
                        selfs: data.selfs,
                        hrefs: data.hrefs,
                        ids: data.ids,
                    }
                    commentCounterP.innerText = Number(commentCounterP.innerText) + 1
                    commentsContainerDiv.parentElement.parentElement.querySelector('#comment-input').value = ''

                    createComment(commentsData, 0, commentsContainerDiv, commentCounterP, true)
                }
            })
    }

}

function createComment(commentsData, i, commentsContainerDiv, commentCounterP, isTop) {

    let ids = commentsData.ids[i]
    let username = commentsData.usernames[i]
    let avatar = commentsData.avatars[i]
    let text = commentsData.texts[i]
    let self = commentsData.selfs[i]
    let data = commentsData.times[i]
    let href = commentsData.hrefs[i]

    let commentContent = document.createElement("div");
    commentContent.classList.add("comment-content");
    commentContent.classList.add('style-' + commentsData.post_id)

    let comAvatar = document.createElement("div");
    comAvatar.classList.add("com-avatar");

    let avatarImg = document.createElement("img");
    avatarImg.classList.add("com-avatar-img");
    avatarImg.src = "/static/avatars/users/" + avatar;
    avatarImg.alt = "";

    let cont = document.createElement("div");
    cont.classList.add("cont");

    let comName = document.createElement("div");
    comName.classList.add("com-name");

    let nameText = document.createElement("b");
    nameText.innerHTML = "<a href='/" + href + "'>" + "<p>" + username + "</p></a>";

    let comText = document.createElement("div");
    comText.classList.add("com-text");
    comText.innerHTML = "<p>" + text + "</p>";

    let comDate = document.createElement("div");
    comDate.classList.add("com-date");

    let deleteDate = document.createElement("p");
    deleteDate.style.color = "#a6a6a6";
    deleteDate.style.fontSize = "14px";
    deleteDate.innerHTML = data;

    comAvatar.appendChild(avatarImg);
    comName.appendChild(nameText);
    comDate.appendChild(deleteDate);

    if (self) {
        let deleteComment = document.createElement("p");
        deleteComment.id = "deleteComment";
        deleteComment.innerHTML = "Удалить";
        deleteComment.style.color = '#a6a6a6'
        deleteComment.style.fontSize = '15px'
        deleteComment.addEventListener('click', function (){
            fetch('comments/delete', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({id: ids})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success){
                        deleteComment.parentElement.parentElement.parentElement.remove()
                        let comCount = commentCounterP.innerText
                        commentCounterP.innerText = Number(comCount) - 1

                    }
                })
        })


        comDate.appendChild(deleteComment);
    }




    cont.appendChild(comName);
    cont.appendChild(comText);
    cont.appendChild(comDate);

    commentContent.appendChild(comAvatar);
    commentContent.appendChild(cont);

    if (!isTop) {
        commentsContainerDiv.appendChild(commentContent);
    }
    else {
        commentsContainerDiv.prepend(commentContent)
    }
}


function likePost(id, likes_div) {
    let data = {id: id}
    fetch('post/like', {
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


function openFile(type, src, event) {
    event.stopPropagation()
    document.getElementById('body').style.opacity = 0.1
    if (type == 'image'){
        document.getElementById('open-photo').classList.remove('hide')
        document.getElementById('open-photo-img').src = src
        document.getElementById('photo_name').innerText = ''
        document.getElementById('open-photo').style.opacity = 1;
        try{
           document.getElementById('delete-photo').classList.add('hide')
        }catch {}


        function handleBodyClick1() {
            document.getElementById('body').style.opacity = 1;
            document.getElementById('open-photo').classList.add('hide');
            document.getElementById('body').removeEventListener('click', handleBodyClick1);
        }

        document.getElementById('body').addEventListener('click', handleBodyClick1);

        function closePhoto1(event){
            if (event.key == 'Escape'){
                handleBodyClick1()
            }
        }
        document.addEventListener('keydown', closePhoto1)
    }
}

function remPost(post_id){


    fetch('post/remove', {
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


function createPost(postData, commentsData, selfAvatar) {
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
                if (postData.group == true){
                    sourceEl.src = `/static/groups/video/${file}`;
                }
                else {
                    sourceEl.src = `/static/users/video/${file}`;
                }
                sourceEl.type = 'video/mp4';
                videoEl.appendChild(sourceEl);
                fileDiv.appendChild(videoEl);
            } else {
                let imgEl = document.createElement('img');
                imgEl.classList.add('post-file-el');
                if (postData.group == true){
                    imgEl.src = `/static/groups/photos/${file}`;
                }
                else {
                    imgEl.src = `/static/users/photos/${file}`;
                }
                imgEl.alt = '';
                imgEl.addEventListener('click', function (event) {
                    openFile(type='image', src=imgEl.src, event)
                })


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
    commentsDiv.addEventListener('click', function () {

    })
    commentsDiv.id = 'comments';
    let commentImg2 = document.createElement('img');
    commentImg2.classList.add('comment-image');
    commentImg2.src = '/static/img/comment.png';
    commentImg2.alt = '';

    let commentCounterP = document.createElement('p');
    commentCounterP.id = 'comment-counter';
    commentCounterP.textContent = postData.comments;

    commentsDiv.appendChild(commentImg2)
    commentsDiv.appendChild(commentCounterP);
    actionsDiv.appendChild(commentsDiv);

    postDiv.appendChild(actionsDiv);



    const commentBlockDiv = document.createElement('div')
    commentBlockDiv.classList.add('hide')


    commentsDiv.addEventListener('click', function () {
        commentBlockDiv.classList.remove('hide')
    })

    const hrElm = document.createElement('hr')
    hrElm.style.marginTop = '20px'
    commentBlockDiv.appendChild(hrElm)

    const commentsContainerDiv = document.createElement('div')
    commentsContainerDiv.id = 'comments-container'

    for (let i = 0; i < commentsData.usernames.length; i++){
        createComment(commentsData, i, commentsContainerDiv, commentCounterP, false)
    }

    commentBlockDiv.appendChild(hrElm)
    commentBlockDiv.appendChild(commentsContainerDiv)

    if (postData.comments > commentBlockDiv.querySelectorAll('.comment-content').length){
        let showNext = document.createElement("p");
        showNext.id = "showNext";
        showNext.innerHTML = "Показать следующие комментарии";
        showNext.style.marginTop = '15px'
        showNext.addEventListener('click', function () {
            let offset = document.querySelectorAll('.style-' + postData.id).length

            fetch('comments/load', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({offset: offset, postId: postData.id})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success){
                        let commentsData = {
                            usernames: data.usernames,
                            avatars: data.avatar_paths,
                            texts: data.texts,
                            times: data.times,
                            selfs: data.selfs,
                            hrefs: data.hrefs,
                            ids: data.ids,
                            post_id: data.post_id
                        }

                        let selfAvatar = data.selfAvatar
                        for (let i = 0; i < commentsData.usernames.length; i++){
                            createComment(commentsData, i, commentsContainerDiv, commentCounterP, false)
                        }

                    }
                })
        })
        commentBlockDiv.appendChild(showNext)
    }


    let commentInput = document.createElement("div");
    commentInput.classList.add("commentInput");

    let commentImg1 = document.createElement("img");
    commentImg1.classList.add("com-avatar-img");

    if (selfAvatar){
        commentImg1.src = `../static/avatars/users/${selfAvatar}`;
    }
    else {
        commentImg1.src = "../static/avatars/default.png";
    }


    commentImg1.alt = "";

    let textarea = document.createElement("textarea");
    textarea.name = "comm";
    textarea.id = "comment-input";
    textarea.rows = "1";

    textarea.addEventListener('input', autoResize);

    function autoResize() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    }


    let sendDiv = document.createElement("div");
    sendDiv.classList.add("send-div");
    sendDiv.addEventListener('click', function () {
        sendComment(textarea.value,commentsContainerDiv, commentCounterP, postData.id)
    })



    let sendBtn = document.createElement("img");
    sendBtn.classList.add("send-btn");
    sendBtn.src = "../static/img/send.png";
    sendBtn.alt = "";


    commentInput.appendChild(commentImg1);
    commentInput.appendChild(textarea);
    sendDiv.appendChild(sendBtn);
    commentInput.appendChild(sendDiv);

    commentBlockDiv.appendChild(commentInput)


    postDiv.appendChild(commentBlockDiv)
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
        setTimeout(function () {
            isAtBottom = false;
        }, 500)
    }
});
async function loadMoreContent(count) {
    let all = false;
    let tag = null;
    if (window.location.pathname == '/') {
        all = true;
    } else {
        if (window.location.pathname.split('/').length == 2) {
            tag = window.location.pathname.split('/')[1];
        }else {
            tag = window.location.pathname.split('/')[2];
        }
    }

    const currenrUrl = window.location.href;
    const urlParams = new URLSearchParams(window.location.search);
    let section = urlParams.get('section');

    let postNext = document.querySelectorAll('.post').length;

    let isGroup;
    if (window.location.pathname.split('/').length == 3 && window.location.pathname.split('/')[1] == 'community'){
        isGroup = true
    }else {
        isGroup = false
        console.log(window.location.pathname.length)
        console.log(window.location.pathname.split('/')[1])
    }
    try {
        const response = await fetch(`/posts/load-more?section=${section}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ startWith: postNext, all: all, count: count, tag: tag, isGroup: isGroup })
        });

        const data = await response.json();

        if (data.success) {
            const commentFetchPromises = data.usernames.map(async (username, i) => {
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
                    liked: data.liked[i],
                    group: data.groups[i]
                };


                const commentsResponse = await fetch('comments/load', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ postId: postData.id, offset: 0 })
                });

                const commentsData = await commentsResponse.json();

                if (commentsData.success) {
                    return {
                        postData,
                        commentsData: {
                            usernames: commentsData.usernames,
                            avatars: commentsData.avatar_paths,
                            texts: commentsData.texts,
                            times: commentsData.times,
                            selfs: commentsData.selfs,
                            hrefs: commentsData.hrefs,
                            ids: commentsData.ids,
                            post_id: commentsData.post_id
                        },
                        selfAvatar: commentsData.selfAvatar
                    };
                }

                return null;
            });

            const results = await Promise.all(commentFetchPromises);

            results.forEach(result => {
                if (result) {
                    createPost(result.postData, result.commentsData, result.selfAvatar);
                }
            });
        }
    } catch (error) {
        console.error('Error:', error);
    }
}


