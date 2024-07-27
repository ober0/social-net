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
        let first_arg = document.querySelector('.active').getAttribute('filter-type')
        let second_arg = document.getElementById('search-input').value


        window.location.href = `/search/${first_arg}?q=${second_arg}`
    }

    let isAtBottom = false;

    window.addEventListener('scroll', function() {
        if ((window.innerHeight + window.scrollY) >= document.body.scrollHeight - 1) {
            if (!isAtBottom) {
                loadMoreContent();
                isAtBottom = true;
            }
        } else {
            setTimeout(function () {
                isAtBottom = false;
            }, 500)
        }
    });

    function loadMoreContent() {
        let el_count = document.querySelectorAll('.content').length
        let first_arg = document.querySelector('.active').getAttribute('filter-type')
        let second_arg = document.getElementById('search-input').value

        let data = {
            count: el_count,
            filter: second_arg
        }
        if (first_arg == 'people'){
            fetch('/search/people/load-more', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success){

                    }
                })
        }
        else if (first_arg == 'community'){
            fetch('/search/community/load-more', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success){
                        console.log(2)
                    }
                })
        }

    }
})