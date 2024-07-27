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
        let first_arg = window.location.pathname.split('/')
        let second_arg = document.getElementById('search-input').value
        first_arg = document.querySelector('.active').getAttribute('filter-type')

        window.location.href = `/search/${first_arg}?q=${second_arg}`
    }
})