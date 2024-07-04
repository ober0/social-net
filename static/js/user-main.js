function go_edit_prifile() {
    window.location.href = '/edit_user'
}

function go_message() {
    window.location.href = '/messanger'
}
document.getElementById('goFriend', function () {
    window.location.href = '/friends?user=' + this.getAttribute('my_tag')
})

document.getElementById('goSubs', function () {
    window.location.href = '/subscribe?user=' + this.getAttribute('my_tag')
})


function addFriend(user_id){
    return 0
}

function remFriend(user_id){
    return 0
}

function about(){
    document.getElementById('body').style.opacity = 0.3;
    document.getElementById('about').style.opacity = 1;
    document.getElementById('about').classList.remove('hide')

}

function hideAbout() {
    document.getElementById('body').style.opacity = 1;
    document.getElementById('about').classList.add('hide')
}


