document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.chats-el').forEach(btn => {
        btn.addEventListener('click', function () {
            window.location.href = '/messanger?chat=' + btn.id
        })
    })
})