function go_edit_prifile() {
    window.location.href = '/edit_user'
}

function go_message() {
    window.location.href = '/messanger'
}

function goFriends(user_id){
    window.location.href = '/friends?user=' + user_id
}
function goSubs(user_id){
    console.log('/subscribe?user=' + user_id)
    window.location.href = '/subscribe?user=' + user_id
}

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


