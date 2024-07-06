document.addEventListener("DOMContentLoaded", () => {
    const socket = io();

    socket.emit('join_main_room', {});

});

