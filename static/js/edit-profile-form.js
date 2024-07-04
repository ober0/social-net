document.getElementById('sendDataInfo').addEventListener('click', function () {
    const first_nameInput = document.getElementById('firstName')
    const second_nameInput = document.getElementById('lastName')
    const tagInput = document.getElementById('tag')
    const genderInput = document.getElementById('gender')
    const birthdayInput = document.getElementById('birthday')
    const countryInput = document.getElementById('country')
    const cityInput = document.getElementById('city')
    const educationInput = document.getElementById('education')
    const education_year_startInput = document.getElementById('education-year-start')
    const education_year_finishInput = document.getElementById('education-year-finish')


    const birthdayChecked = document.getElementById('agreement-birthday').checked;
    const genderChecked = document.getElementById('agreement-gender').checked;
    const learnChecked = document.getElementById('agreement-learn').checked;
    const cityChecked = document.getElementById('agreement-city').checked;
    try{
        const agreementChecked = document.getElementById('agreement').checked;
    }
    catch{}

    const inputs = [
      first_nameInput, second_nameInput, document.getElementById('tag2'), genderInput, birthdayInput,
      countryInput, cityInput, educationInput, education_year_startInput, education_year_finishInput, document.getElementById('avatar-input')
    ];

    inputs.forEach(input => {
      if (input) {
        input.style.border = '1px solid lightgreen';
      }
    });


    document.getElementById('firstNameError').classList.add('hide')
    document.getElementById('lastNameError').classList.add('hide')
    document.getElementById('tagError').classList.add('hide')
    document.getElementById('genderError').classList.add('hide')
    document.getElementById('birthdayError').classList.add('hide')
    document.getElementById('countryError').classList.add('hide')
    document.getElementById('cityError').classList.add('hide')
    document.getElementById('education-year-startError').classList.add('hide')
    document.getElementById('education-year-finishError').classList.add('hide')
    document.getElementById('avatarError').classList.add('hide')
    try{
        document.getElementById('agreementError').classList.add('hide')
    }
    catch {}

    document.getElementById('allError').classList.add('hide')

    let isValid = true;

    if (!/[а-яА-Я]/.test(first_nameInput.value)){
        first_nameInput.style.border = '1px solid red'
        document.getElementById('firstNameError').classList.remove('hide')
        document.getElementById('firstNameError').innerText = 'Имя может состоять только из русских букв'
        isValid = false;
    }
    if (first_nameInput.value.length < 2){
        first_nameInput.style.border = '1px solid red'
        document.getElementById('firstNameError').classList.remove('hide')
        document.getElementById('firstNameError').innerText = 'Имя должно быть минимум из 2 букв'
        isValid = false;
    }

    if (!/[а-яА-Я]/.test(second_nameInput.value)){
        second_nameInput.style.border = '1px solid red'
        document.getElementById('lastNameError').classList.remove('hide')
        document.getElementById('lastNameError').innerText = 'Фамилия может состоять только из русских букв'
        isValid = false;
    }
    if (second_nameInput.value.length < 1){
        second_nameInput.style.border = '1px solid red'
        document.getElementById('lastNameError').classList.remove('hide')
        document.getElementById('lastNameError').innerText = 'Поле не может быть пустым'
        isValid = false;
    }

    if (!/^[a-z0-9_]+$/.test(tag.value)) {
        document.getElementById('tag2').style.border = '1px solid red'
        document.getElementById('tagError').classList.remove('hide')
        document.getElementById('tagError').innerText = 'Тег может состоять только из маленьких латинских букв, цифр и нижнего подчеркивания'
        isValid = false;
    }
    else{

        if (tag.value.length > 2){
             const data = {
                 tag: tag.value
             }
             fetch('/checkUniqueTag', {
                 method: 'post',
                 headers: {'Content-Type': 'application/json'},
                 body: JSON.stringify(data)
             })
                 .then(response => response.json())
                 .then(result => {
                     if(!result.result){
                         document.getElementById('tag2').style.border = '1px solid red'
                         document.getElementById('tagError').classList.remove('hide')
                         document.getElementById('tagError').innerText = 'Этот тег уже занят'
                         isValid = false;
                     }
                 })
        }
        else {
            document.getElementById('tag2').style.border = '1px solid red'
            document.getElementById('tagError').classList.remove('hide')
            document.getElementById('tagError').innerText = 'Тег должен состоять минимум из 3 символов'
            isValid = false;
        }



    }

    if (!genderInput.value){
        genderInput.style.border = '1px solid red'

        document.getElementById('genderError').classList.remove('hide')
        document.getElementById('genderError').innerText = 'Пол обязателен к заполнению'
        isValid = false;
    }

    if(birthdayInput.value.length < 1){
        birthdayInput.style.border = '1px solid red'
        document.getElementById('birthdayError').classList.remove('hide')
        document.getElementById('birthdayError').innerText = 'Дата рождения обязательна к заполнению'
        isValid = false;
    }
    
    if(!/^[а-яА-Яa-zA-Z]+$/.test(countryInput.value)){
        countryInput.style.border = '1px solid red'
        document.getElementById('countryError').classList.remove('hide')
        document.getElementById('countryError').innerText = 'В названии страны могут быть только буквы'
        isValid = false;
    }
    
    if(countryInput.value.length < 1){
        countryInput.style.border = '1px solid red'
        document.getElementById('countryError').classList.remove('hide')
        document.getElementById('countryError').innerText = 'Страна проживания обязательна к заполнению'
        isValid = false;
    }
    
    if (cityInput.value.length > 0){
        if(!/^[а-яА-Яa-zA-Z]+$/.test(cityInput.value)){
            cityInput.style.border = '1px solid red'
            document.getElementById('cityError').classList.remove('hide')
            document.getElementById('cityError').innerText = 'В названии города могут быть только буквы'
            isValid = false;
        }
    }


    if (education_year_finishInput.value.value > 0){
        if (!/^\d{4}$/.test(education_year_startInput.value)) {
            education_year_startInput.style.border = '1px solid red';
            document.getElementById('education-year-startError').classList.remove('hide');
            document.getElementById('education-year-startError').innerText = 'Введите год начала обучения, в формате yyyy';
            isValid = false;
        }
    }


    if (education_year_finishInput.value.value > 0){
        if (!/^\d{4}$/.test(education_year_finishInput.value)) {
            education_year_finishInput.style.border = '1px solid red';
            document.getElementById('education-year-finishError').classList.remove('hide');
            document.getElementById('education-year-finishError').innerText = 'Введите год окончания обучения, в формате yyyy';
            isValid = false;
        }
    }

    try{
        if (!agreementChecked){
             document.getElementById('agreementError').classList.remove('hide')
             document.getElementById('agreementError').innerText = 'Согласитесь с условиями для продолжения'
             isValid = false;
        }
    }
    catch {}


    let avatar = document.getElementById('avatar-input').files[0]

    try{
        let avatar_type = avatar.type
        const allowedTypes = ['image/png', 'image/jpeg', 'image/gif'];
        if (avatar){
            if (!allowedTypes.includes(avatar_type)){
                 document.getElementById('avatarError').classList.remove('hide')
                 document.getElementById('avatarError').innerText = 'Доступны только файлы .gif .png .jpg'
                 document.getElementById('avatar-input').style.border = '1px solid red'
                 isValid = false;
            }
        }
    }
    catch {}


    if (isValid){
         let avatar = document.getElementById('avatar-input').files[0]

         const socket = io()
         socket.emit('edit_profile_save', {
             name: first_nameInput.value,
             second_name: second_nameInput.value,
             tag: tagInput.value,
             gender: genderInput.value,
             birthday: birthdayInput.value,
             country: countryInput.value,
             city: cityInput.value,
             education_place: educationInput.value,
             education_start: education_year_startInput.value,
             education_end: education_year_finishInput.value,
             show_birthday: birthdayChecked,
             show_gender: genderChecked,
             show_education: learnChecked,
             show_address: cityChecked,
             file: avatar
        })




        socket.on('edit_profile_save_result', (data) => {
            if (data.result){
                let tag = data.tag
                window.location.href = '/' + tag
            }
            else{
                let error = document.getElementById('allError')
                error.innerText = data.error
                error.classList.remove('hide')
                if (data.error == 'Пользователь не найден: ошибка доступа'){
                    setTimeout(function () {
                        window.location.href = '/'
                    }, 5000)
                }
            }
        })

    }



})