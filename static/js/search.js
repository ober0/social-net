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
})