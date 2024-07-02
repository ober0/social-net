document.getElementById('sendData').addEventListener('click', function () {
    document.getElementById('code-error').innerText = ''
    let code = document.getElementById('code')

    fetch('/confirm_email', {
        method: 'post',
        headers: {
                'Content-Type': 'application/json'
            },
        body: JSON.stringify(code.value)
    })
        .then(response => response.json())

        .then(result => {
            if (result.res){
                window.location.href = '/'
            }

            else {
                code.innerText = ''
                document.getElementById('code-error').innerText = 'Не верный код'
            }
        })
})


const link = document.getElementById('codeTry');
let time = 60000; // 60 секунд

function updateLink() {
    if (time > 0) {
        time -= 1000;
        link.innerText = 'Получить код заново через ' + (time / 1000) + ' сек';
    } else {
        link.classList.remove('disabled');
        link.innerText = 'Получить код заново';
        clearInterval(interval);
    }
}

const interval = setInterval(updateLink, 1000);