const photo_btn = document.getElementById('photo-btn')
const music_btn = document.getElementById('music-btn')
const video_btn = document.getElementById('video-btn')

const photo_content = document.getElementById('sec-1-content-photo')
const music_content = document.getElementById('sec-1-content-music')
const video_content = document.getElementById('sec-1-content-video')


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

document.getElementById('open-all-photo').addEventListener('click', function () {
    window.location.href = '/photos?user=' + this.getAttribute('tag')
})
document.getElementById('open-all-music').addEventListener('click', function () {
    window.location.href = '/music?user=' + this.getAttribute('tag')
})
document.getElementById('open-all-video').addEventListener('click', function () {
    window.location.href = '/video?user=' + this.getAttribute('tag')
})


function newVideo() {
    window.location.href = '/video/add'
}


function cancelLoad() {
    document.getElementById('body').style.opacity = 1;
    document.getElementById('new-photo-menu').classList.add('hide');
    let filesToRemove = document.querySelectorAll('.new-photo-img')
    filesToRemove.forEach(file => {
        file.remove()
    })
    document.getElementById('cancel-load-photo').removeEventListener('click', cancelLoad)
}


function newPhoto() {
    console.log(1)
    document.getElementById('newPhoto-input').click()
}

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


socketio.on('newPhoto_result', (data) => {
    if (data.success){
        document.getElementById('body').style.opacity = 0.2;
        document.getElementById('new-photo-menu').classList.remove('hide');
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
                console.log(2)
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
