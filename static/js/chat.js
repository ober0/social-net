document.addEventListener('DOMContentLoaded', function (){
    let scrollbar = document.querySelector('.message-container')
    scrollbar.scrollTop = scrollbar.scrollHeight

    document.querySelector('.chat-back').addEventListener('click', function (){
        window.location.href = '/messanger'
    })
})