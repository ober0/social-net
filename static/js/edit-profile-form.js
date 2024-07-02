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
    const agreementChecked = document.getElementById('agreement').checked;


    const inputs = [
      first_nameInput, second_nameInput, tagInput, genderInput, birthdayInput,
      countryInput, cityInput, educationInput, education_year_startInput, education_year_finishInput
    ];

    inputs.forEach(input => {
      if (input) {
        input.style.border = '1px solid #dee2e6';
      }
    });


    first_nameInput.classList.add('hide')
    second_nameInput.classList.add('hide')
    tagInput.classList.add('hide')
    genderInput.classList.add('hide')
    birthdayInput.classList.add('hide')
    countryInput.classList.add('hide')
    cityInput.classList.add('hide')
    education_year_startInput.classList.add('hide')
    education_year_finishInput.classList.add('hide')

    let isValid = true;

    if (!/[а-яА-Я]/.test(first_nameInput.value)){
        first_nameInput.style.border = '1px solid red'
        first_nameInput.classList.remove('hide')
        document.getElementById('firstNameError').innerText = 'Имя может состоять только из русских букв'
        isValid = false;
    }
    if (first_nameInput.value.length < 2){
        first_nameInput.style.border = '1px solid red'
        first_nameInput.classList.remove('hide')
        document.getElementById('firstNameError').innerText = 'Имя должно быть минимум из 2 букв'
        isValid = false;
    }

    if (!/[а-яА-Я]/.test(second_nameInput.value)){
        second_nameInput.style.border = '1px solid red'
        second_nameInput.classList.remove('hide')
        document.getElementById('lastNameError').innerText = 'Фамилия может состоять только из русских букв'
        isValid = false;
    }
    if (second_nameInput.value.length < 1){
        second_nameInput.style.border = '1px solid red'
        second_nameInput.classList.remove('hide')
        document.getElementById('lastNameError').innerText = 'Поле не может быть пустым'
        isValid = false;
    }

    if (/[a-zA-Z0-9]/.test(tag.value)){
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
                         tagInput.style.border = '1px solid red'
                         tagInput.classList.remove('hide')
                         document.getElementById('tagError').innerText = 'Этот тег уже занят'
                         isValid = false;
                     }
                 })
        }
        else {
            tagInput.style.border = '1px solid red'
            tagInput.classList.remove('hide')
            document.getElementById('tagError').innerText = 'Тег должен состоять минимум из 3 символов'
            isValid = false;

        }

    }
    else{
        tagInput.style.border = '1px solid red'
        tagInput.classList.remove('hide')
        document.getElementById('tagError').innerText = 'Тег может состоять только из латинских букв и цифр'
        isValid = false;

    }

    if (!genderInput.checked){
        genderInput.style.border = '1px solid red'
        genderInput.classList.remove('hide')
        document.getElementById('genderError').innerText = 'Пол обязателен к заполнению'
        isValid = false;
    }

    if(birthdayInput.value.length < 1){
        birthdayInput.style.border = '1px solid red'
        birthdayInput.classList.remove('hide')
        document.getElementById('birthdayError').innerText = 'Дата рождения обязательна к заполнению'
        isValid = false;
    }

    if(countryInput.value.length < 1){
        countryInput.style.border = '1px solid red'
        countryInput.classList.remove('hide')
        document.getElementById('countryError').innerText = 'Страна проживания обязательна к заполнению'
        isValid = false;
    }
    if(/[а-яА-Яa-zA-Z]/.test(countryInput.value)){
        countryInput.style.border = '1px solid red'
        countryInput.classList.remove('hide')
        document.getElementById('countryError').innerText = 'В названии страны могут быть только буквы'
        isValid = false;
    }

    if(/[а-яА-Яa-zA-Z]/.test(cityInput.value)){
        cityInput.style.border = '1px solid red'
        cityInput.classList.remove('hide')
        document.getElementById('cityError').innerText = 'В названии города могут быть только буквы'
        isValid = false;
    }

     if(/\n/.test(education_year_startInput.value) && education_year_startInput.value.length == 4){
        education_year_startInput.style.border = '1px solid red'
        education_year_startInput.classList.remove('hide')
        document.getElementById('education-year-startError').innerText = 'Введите год начала обучения, в формате yyyy'
        isValid = false;
     }

     if(/\n/.test(education_year_finishInput.value) && education_year_finishInput.value.length == 4){
        education_year_finishInput.style.border = '1px solid red'
        education_year_finishInput.classList.remove('hide')
        document.getElementById('education-year-finishError-startError').innerText = 'Введите год окончания обучения, в формате yyyy'
        isValid = false;
     }


     if (!agreementChecked){
         agreementChecked.classList.remove('hide')
         document.getElementById('agreementError').innerText = 'Согласитесь с условиями для продолжения'
         isValid = false;
     }




})