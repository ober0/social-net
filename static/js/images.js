function closeWindow(window_id) {
    document.getElementById('body').style.opacity = 1;
    document.getElementById(window_id).classList.add('hide');
}
const socketio = io()
let photos = document.querySelectorAll('.image')
photos.forEach(photo => {
    photo.addEventListener('click', function (event) {
        event.stopPropagation()
        document.getElementById('open-photo').classList.remove('hide')
        document.getElementById('open-photo-img').src = photo.src
        document.getElementById('photo_name').innerText = photo.getAttribute('filename')
        document.getElementById('open-photo').style.opacity = 1;
        document.getElementById('delete-photo').classList.remove('hide')

        document.getElementById('body').style.opacity = 0.1;
        let photo_id = photo.getAttribute('photo-id')

        document.getElementById('delete-photo').setAttribute('photo-id', photo_id)
         function handleBodyClick() {
            closeWindow('open-photo');
            document.getElementById('body').removeEventListener('click', handleBodyClick);
        }

        document.getElementById('body').addEventListener('click', handleBodyClick);

        function closePhoto(event){
            if (event.key == 'Escape'){
                handleBodyClick()
            }
        }
        document.addEventListener('keydown', closePhoto)
    })
})

try {
    document.getElementById('delete-photo').addEventListener('click', function () {
        socketio.emit('deletePhoto', {photo_id: this.getAttribute('photo-id')})
    })

    document.querySelectorAll('.delete-photo').forEach(btn => {
        btn.addEventListener('click', function () {
            socketio.emit('deletePhoto', {photo_id: this.getAttribute('photo-id')})
        })
    })
    socketio.on('deletePhoto_result', (data) => {
        if (data.success) {
            document.getElementById('body').click()
            location.reload()
        } else {
            alert(data.error)
        }
    })
}catch {}