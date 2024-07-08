document.addEventListener('DOMContentLoaded', function () {
    let searchInput = document.getElementById('search-main')

    const soc = io()

    searchInput.addEventListener('input', function () {
        let searchValue = searchInput.value
        soc.emit('search', {data:searchValue})
    })

    soc.on('search_result', (data) => {
        if (data.success){
            console.log(data)
        }

    })
})