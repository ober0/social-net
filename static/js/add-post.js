function openPhotoInput(){
    document.getElementById('photoInput').click()
}

function openVideoInput(){
    document.getElementById('videoInput').click()
}



document.addEventListener('DOMContentLoaded', function (){

    
    function hideAll(){
        document.getElementById('photos').classList.add('hide')
        document.getElementById('addpost-bottom').classList.add('hide')
        document.getElementById('text-new-input').style.marginBottom = '0'
        document.getElementById('body').removeEventListener('click', hideAll)
        document.getElementById('text-new-input').addEventListener('click', openAll)
        document.removeEventListener('keydown', hideAllEsc)
        $('#text-new-input').css('height', '55px')
    }

    function hideAllEsc(event){
        if (event.key === 'Escape'){
            hideAll()
        }
    }

    function openAll(){
        if (document.querySelectorAll('.addpost-user-content').length > 0){
            document.getElementById('photos').classList.remove('hide')
        }
        document.getElementById('search_result').classList.add('hide')
        document.getElementById('notifications').classList.add('hide')
        document.getElementById('right-info').classList.add('hide')
        document.getElementById('addpost-bottom').classList.remove('hide')
        document.getElementById('text-new-input').style.marginBottom = '10px'
        document.getElementById('text-new-input').focus()
        document.getElementById('addpost-container').addEventListener('click', function (event) {
            event.stopPropagation()
        })
        document.getElementById('body').addEventListener('click', hideAll)
        document.addEventListener('keydown', hideAllEsc)

        const textarea = document.getElementById('text-new-input')
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';

    }
    document.getElementById('text-new-input').addEventListener('click', openAll)

    const textarea = document.getElementById('text-new-input')
    textarea.addEventListener('input', function() {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    });


    document.getElementById('addpost-right-menu').addEventListener('click', function () {
        openAll()
    })

    function newFile() {
        const parentPhoto = document.getElementById('photo-content')

        const file = this.files[0]

        if (file){
            const reader = new FileReader()

            reader.onload = function (event) {
                let file_count = document.querySelectorAll('.addpost-user-content').length
                if (file_count < 8){
                    document.getElementById('photos').classList.remove('hide')

                    let photo_container = document.createElement('div')

                    let photo;
                    if (file.type.split('/')[0] == 'image'){
                         photo = document.createElement('img')
                         photo.classList.add('photo')
                    }
                    else if (file.type.split('/')[0] == 'video'){
                        photo = document.createElement('video')
                        photo.controls = true;
                        photo.classList.add('video')
                    }
                    photo.classList.add('addpost-user-content')

                    photo.src = event.target.result

                    let removeButtonContainer = document.createElement('div')
                    removeButtonContainer.classList.add('removeButtonContainer')

                    let removeButton = document.createElement('div');
                    removeButton.style.margin = 0
                    removeButton.innerText = 'x';
                    removeButton.style.position = 'relative'
                    removeButton.style.bottom = '2px'
                    removeButtonContainer.appendChild(removeButton)

                    function checkCount() {
                        if (document.querySelectorAll('.addpost-user-content').length == 0){
                            document.getElementById('photos').classList.add('hide')
                        }
                    }

                    removeButtonContainer.addEventListener('click', function (){
                        photo_container.remove()
                        checkCount()
                    })

                    photo_container.appendChild(removeButtonContainer)
                    photo_container.appendChild(photo)
                    photo_container.classList.add('photo-rem')
                    parentPhoto.appendChild(photo_container)



                }
                else {
                    alert('Максимум 8 файлов')
                }

            }

            reader.readAsDataURL(file);

            this.value = ''
        }


    }

    $('#cancel-addpost').click(function (){
        console.log(1)
        $('#text-new-input').val('')
        $('#photo-content').empty()
        hideAll()
    })
    
    document.getElementById('publicate-post').addEventListener('click', function () {
        let text = document.getElementById('text-new-input').value;
        let photos = document.querySelectorAll('.photo');
        let videos = document.querySelectorAll('.video');
        let isPublic = !document.getElementById('no-publ').checked;

        let photos_src= [];
        let videos_src = [];


        photos.forEach(photo => {
            photos_src.push(photo.src)
        })

        videos.forEach(video => {
            videos_src.push(video.src)
        })

        const data = {
            text: text,
            isPublic: isPublic,
            photos: photos_src,
            videos: videos_src
        }

        fetch('/addPost', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })

            .then(response => response.json())
            .then(data => {
                console.log(data.result);
            })

    });



    document.getElementById('photoInput').addEventListener('input', newFile)
    document.getElementById('videoInput').addEventListener('input', newFile)
})