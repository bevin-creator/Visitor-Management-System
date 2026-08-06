function validateRegistrationForm(){
    const fullName = document.getElementById("full_name");
    const email = document.getElementById("email");
    const phone = document.getElementById("phone");
    

    let isValid = true;
    clearErrors();

    if (fullName.value.trim().length < 2){
        showError(fullName, "NAme must be at least 2 Characters");
        isValid=false;
    }

    if (!email.value.includes("@") || !email.value.includes(".")) {
        showError(email, "Please enter a valid email address!");
        isValid=false;
    }

    if (phone.value.trim().length <10 || phone.value.trim().length >13) {
        showError(phone, "Please enter a valid phone number!");
        isValid=false;
    }

    return isValid;
}

function showError(input, message){
    const errorSpan = document.createElement("span");
    errorSpan.className= "field-error";
    errorSpan.textContent= message;
    input.parentNode.insertBefore(errorSpan, input.nextSibling);
    input.style.borderColor = "red";
}

function clearErrors(){
    document.querySelectorAll(".field-error").forEach(element => element.remove());
    document.querySelectorAll("input, select").forEach(element => element.style.borderColor="");
}