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

    const first_nameValue = first_nameInput.value;
    const second_nameValue = second_nameInput.value;
    const tagValue = tagInput.value;
    const genderValue = genderInput.value;
    const birthdayValue = birthdayInput.value;
    const countryValue = countryInput.value;
    const cityValue = cityInput.value;
    const educationValue = document.getElementById('education').value;
    const education_year_startValue = document.getElementById('education-year-start').value;
    const education_year_finishValue = document.getElementById('education-year-finish').value;

})