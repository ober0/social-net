document.getElementById('me').addEventListener('click', function () {
    console.log(1)
    window.location.href = '/' + this.getAttribute('my_tag')
})

document.getElementById('news').addEventListener('click', function () {
    window.location.href = '/'
})

document.getElementById('chats').addEventListener('click', function () {
    window.location.href = '/messanger'
})

document.getElementById('friends').addEventListener('click', function () {
    window.location.href = '/friends?user=' + this.getAttribute('my_tag')
})

document.getElementById('soob').addEventListener('click', function () {
    window.location.href = '/groups?user=' + this.getAttribute('my_tag')
})


document.getElementById('photo').addEventListener('click', function () {
    window.location.href = '/photos?user=' + this.getAttribute('my_tag')
})

document.getElementById('video').addEventListener('click', function () {
    window.location.href = '/video?user=' + this.getAttribute('my_tag')
})

document.getElementById('search').addEventListener('click', function () {
    window.location.href = '/search/people'
})

document.getElementById('add-community').addEventListener('click', function () {
    window.location.href = '/new-community'
})

document.getElementById('setting').addEventListener('click', function () {
    window.location.href = '/setting'
})

document.getElementById('support').addEventListener('click', function () {
    window.location.href = '/support'
})