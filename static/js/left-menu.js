document.getElementById('me').addEventListener('click', function () {
    console.log(1)
    window.location.href = '/' + this.getAttribute('my_tag')
})

document.getElementById('news').addEventListener('click', function () {
    window.location.href = '/'
})

document.getElementById('chats').addEventListener('click', function () {
    window.location.href = '/chats'
})

document.getElementById('friends').addEventListener('click', function () {
    window.location.href = '/friends?user=' + this.getAttribute('my_tag')
})