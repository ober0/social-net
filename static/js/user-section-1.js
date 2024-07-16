const photo_btn = document.getElementById('photo-btn')
const music_btn = document.getElementById('music-btn')
const video_btn = document.getElementById('video-btn')

const photo_content = document.getElementById('sec-1-content-photo')
const music_content = document.getElementById('sec-1-content-music')
const video_content = document.getElementById('sec-1-content-video')


function closeWindow(window_id) {
    document.getElementById('body').style.opacity = 1;
    document.getElementById(window_id).classList.add('hide');
}


photo_btn.addEventListener('click', function () {
    music_btn.classList.remove('btn-active')
    video_btn.classList.remove('btn-active')
    photo_btn.classList.add('btn-active')
    photo_content.classList.remove('sec1-content-hide')
    music_content.classList.add('sec1-content-hide')
    video_content.classList.add('sec1-content-hide')
})

music_btn.addEventListener('click', function () {
    music_btn.classList.add('btn-active')
    video_btn.classList.remove('btn-active')
    photo_btn.classList.remove('btn-active')
    photo_content.classList.add('sec1-content-hide')
    music_content.classList.remove('sec1-content-hide')
    video_content.classList.add('sec1-content-hide')
})

video_btn.addEventListener('click', function () {
    music_btn.classList.remove('btn-active')
    video_btn.classList.add('btn-active')
    photo_btn.classList.remove('btn-active')
    photo_content.classList.add('sec1-content-hide')
    music_content.classList.add('sec1-content-hide')
    video_content.classList.remove('sec1-content-hide')
})
try {
    document.getElementById('open-all-photo').addEventListener('click', function () {
        window.location.href = '/photos?user=' + this.getAttribute('tag')
    })
}catch {}
try {
    document.getElementById('open-all-music').addEventListener('click', function () {
        window.location.href = '/music?user=' + this.getAttribute('tag')
    })
}catch {}
try {
    document.getElementById('open-all-video').addEventListener('click', function () {
        window.location.href = '/video?user=' + this.getAttribute('tag')
    })
}catch {}





function newPhoto() {
    document.getElementById('newPhoto-input').click()
}

function cancelLoad() {
    document.getElementById('body').style.opacity = 1;
    document.getElementById('new-photo-menu').classList.add('hide');
    let filesToRemove = document.querySelectorAll('.new-photo-img')
    filesToRemove.forEach(file => {
        file.remove()
    })
    document.getElementById('filesCounter').innerText = '1 Фото'
}



socketio.on('newPhoto_result', (data) => {
    if (data.success){
        document.getElementById('body').style.opacity = 0.1;
        document.getElementById('new-photo-menu').classList.remove('hide');
        function closeWindowPhoto(event){
            if (event.key == 'Escape'){
                cancelLoad()
            }
        }
        document.addEventListener('keydown', closeWindowPhoto)
        function handleBodyClick() {
            cancelLoad();
            document.removeEventListener('keydown', closeWindowPhoto)
            document.getElementById('body').removeEventListener('click', handleBodyClick);
        }

        document.getElementById('body').addEventListener('click', handleBodyClick);
        let file = document.getElementById('newPhoto-input').files[0]

        if (file){
            let reader = new FileReader();

            reader.onload = function (e){
                let parent = document.getElementById('photo-container')
                let newImg = document.createElement('img')
                newImg.src = e.target.result
                newImg.classList.add('new-photo-img')
                newImg.width = 200
                newImg.height = 200
                newImg.setAttribute('filename', file.name)
                parent.appendChild(newImg)
                document.getElementById('newPhoto-input').value = ''
            }
            reader.readAsDataURL(file);
        }

    }
    else {
        alert(data.error)
    }
})


document.getElementById('add-new-photo').addEventListener('click', function () {
    document.getElementById('add_new_photo-input').click()
})


document.getElementById('add_new_photo-input').addEventListener('change', function () {
    let reader = new FileReader()

    let fileTypesAccess = ['image/png', 'image/jpeg'];
    let file = this.files[0]
    if (file) {
        if (fileTypesAccess.includes(this.files[0].type)) {
             reader.onload = function (e){
                let parent = document.getElementById('photo-container')
                let newImg = document.createElement('img')
                newImg.src = e.target.result
                newImg.classList.add('new-photo-img')
                newImg.width = 200
                newImg.height = 200
                newImg.setAttribute('filename', file.name)
                parent.appendChild(newImg)

                let allFiles = document.querySelectorAll('.new-photo-img')
                let filesCount = allFiles.length
                document.getElementById('filesCounter').innerText = filesCount + " Фото"
            }
            reader.readAsDataURL(file);
            this.value = ''
        }
        else {
            alert('Недопустимый тип файла. Пожалуйста, выберите файл .png или .jpg')
        }
    }
})

document.getElementById('go-load-photo').addEventListener('click', function () {
    let files = document.querySelectorAll('.new-photo-img')

    let files_list = []
    let filenames_list = []

    files.forEach(file => {
        files_list.push(file.src)
        filenames_list.push(file.getAttribute('filename'))
    })
    socketio.emit('newPhotos_all', {files: files_list, filenames: filenames_list})
})

document.getElementById('cancel-load-photo').addEventListener('click', cancelLoad)


socketio.on('newPhoto_all_result', (data) => {
    if (data.success){
        cancelLoad()
        location.reload()
    }
    else {
        cancelLoad()
        alert('Произошла ошибка загрузки: ' + data.error)
    }
})




let photos = document.querySelectorAll('.sec-1-photo')
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

    socketio.on('deletePhoto_result', (data) => {
        if (data.success) {
            document.getElementById('body').click()
            location.reload()
        } else {
            alert(data.error)
        }
    })
}catch {}

try {
    document.getElementById('delete-video').addEventListener('click', function () {
        let el = this
        let videos = document.querySelectorAll('.sec-1-video')
        videos.forEach(video => {
            if (video.getAttribute('video_id') == el.getAttribute('video-id')) {
                video.parentNode.remove()
                document.getElementById('body').click()
            }
        })
        let data = {
            video_id: this.getAttribute('video-id')
        }
        fetch('/deleteVideo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    video.remove()
                }
                else {
                    alert(data.error)
                }
            })
    })
}catch {}




let videos = document.querySelectorAll('.sec-1-video')
videos.forEach(video => {
    video.addEventListener('click', function (event) {
        event.stopPropagation()
        document.getElementById('open-video').classList.remove('hide')
        let url = new URL(video.src)

        document.getElementById('open-video-img').src = url.pathname
        document.getElementById('opened-video').load()
        document.getElementById('video_name').innerText = video.getAttribute('name')
        document.getElementById('open-video').style.opacity = 1;
        document.getElementById('body').style.opacity = 0.1;
        let video_id = video.getAttribute('video_id')

        document.getElementById('delete-video').setAttribute('video-id', video_id)
         function handleBodyClick() {
            document.getElementById('opened-video').pause();
            closeWindow('open-video');
            document.getElementById('body').removeEventListener('click', handleBodyClick);
        }

        document.getElementById('body').addEventListener('click', handleBodyClick);

        function closeVideo(event){
            if (event.key == 'Escape'){
                handleBodyClick()
            }
        }
        document.addEventListener('keydown', closeVideo)
    })
})



try {

    document.getElementById('newPhoto-input').addEventListener('change', function (event) {
        const file = event.target.files[0];

        let fileTypesAccess = ['image/png', 'image/jpeg'];
        if (file) {
            if (fileTypesAccess.includes(file.type)) {
                socketio.emit('newPhoto', {
                    file: file,
                    filename: file.name
                });
            } else {
                alert('Недопустимый тип файла. Пожалуйста, выберите файл .png или .jpg')
            }
        }
    });
}catch{}




