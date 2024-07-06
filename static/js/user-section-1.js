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

function newPhoto() {
    window.location.href = '/photos/add'
}

function newVideo() {
    window.location.href = '/video/add'
}