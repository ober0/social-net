document.addEventListener('DOMContentLoaded', function (){
    document.querySelectorAll('.value').forEach(btn => {
        btn.addEventListener('click', function () {
            if (btn.getAttribute('val') == 1){
                btn.setAttribute('val', 0)
                btn.innerText = 'Нет'

            }
            else {
                btn.setAttribute('val', 1)
                btn.innerText = 'Да'
            }

            let data = {
                type: btn.id,
                val: btn.getAttribute('val')
            }

            fetch('/setting/notification/update', {
                method: 'POST',
                body: JSON.stringify(data),
                headers: {
                    'Content-Type': 'application/json'
                }

            })
                .then(response => response.json())
                .then(result => {
                    if (!result.success){
                        alert('Произошла ошибка. Изменения не сохранены')
                    }
                })

        })



    })

})