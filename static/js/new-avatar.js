document.getElementById('avatar-input').addEventListener('change', function (event) {
     let avatarFile = event.target.files[0];


     if (avatarFile) {
          const allowedTypes = ['image/png', 'image/jpeg', 'image/gif'];
          try{
               if (!allowedTypes.includes(avatarFile.type)) {
               document.getElementById('avatarError').classList.remove('hide')
               document.getElementById('avatarError').innerText = 'Доступны только файлы .gif .png .jpg'
               }
               else {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                         const img = document.getElementById('avatar-img');
                         img.src = e.target.result;
                    };
                    reader.readAsDataURL(avatarFile);
               }
          }
          catch {}

     }
})

     function changeAvatar(e) {
          document.getElementById('change-avatar-btn').classList.add('hide')
          document.getElementById('avatar-input').classList.remove('hide')
     }