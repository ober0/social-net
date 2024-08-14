document.addEventListener('DOMContentLoaded', function (){
    let scrollbar = document.querySelector('.message-container')
    scrollbar.scrollTop = scrollbar.scrollHeight

     document.addEventListener('keydown', function (event){
        if(event.key === 'Escape'){
             window.location.href = '/messanger'
        }
    })

    document.querySelector('.chat-back').addEventListener('click', function (){
        window.location.href = '/messanger'
    })

    let isMessageInputActive = false

    document.getElementById('message-input').addEventListener('focus', function () {
        isMessageInputActive = true
    })

    document.getElementById('message-input').addEventListener('blur', function () {
        isMessageInputActive = false
    })

    document.addEventListener('keydown', function (event){
        if(event.key === 'Enter'){}
    })
})