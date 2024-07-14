function createPost(postData){
    console.log(postData)
}






let isAtBottom = false;

window.addEventListener('scroll', function() {
    if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight - 1) {
        if (!isAtBottom) {
            console.log('Пользователь достиг конца страницы');
            loadMoreContent();
            isAtBottom = true;
        }
    } else {
        isAtBottom = false;
    }
});

function loadMoreContent() {
    let postNext = document.querySelectorAll('.post').length
    fetch('/loadMorePosts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({startWith: postNext})
    })
        .then(response => response.json())
        .then(data => {
            if (data.success){
                console.log(data)
                for (let i = 0; i < data.usernames.length; i++){

                    let postData = {
                        username: data.usernames[i],
                        avatar: data.avatars[i],
                        text: data.text[i],
                        files: data.files[i],
                        date: data.dates[i],
                        likes: data.likes[i],
                        comments: data.comments[i],
                        href: data.href[i]
                    }
                    createPost(postData)
                }
            }
        })
}