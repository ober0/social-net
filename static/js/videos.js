function closeWindow(window_id) {
    document.getElementById('body').style.opacity = 1;
    document.getElementById(window_id).classList.add('hide');
}
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
        fetch('/video/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    window.location.reload()
                }
                else {
                    alert(data.error)
                }
            })
    })
}catch {}

try{
    document.querySelectorAll('.delete-video').forEach(btn => {
        btn.addEventListener('click', function (){
            const data = {
            video_id: this.getAttribute('video-id')
        }
        fetch('/video/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                if (data.success){
                    this.parentElement.remove()
                }
                else {
                    alert(data.error)
                }
            })
        })
    })
}catch {}


let videos = document.querySelectorAll('.video')
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