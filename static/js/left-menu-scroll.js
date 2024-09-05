document.addEventListener('DOMContentLoaded', function () {
    const left_menu = document.getElementById('main')
    left_menu.style.position = 'relative'
    document.addEventListener('scroll', function () {
        let scrollHeight = window.scrollY
        console.log(d)
        left_menu.style.top = left_menu.style.top + scrollHeight + 'px'
    })

})