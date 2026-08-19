// Cloud Book Exchange - JavaScript

document.addEventListener("DOMContentLoaded", function () {

    console.log("Cloud Book Exchange loaded successfully.");

    // Form validation
    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const inputs = form.querySelectorAll(
                "input[required], select[required]"
            );

            let valid = true;

            inputs.forEach(function (input) {

                if (input.value.trim() === "") {
                    valid = false;
                    input.style.border = "2px solid red";
                } else {
                    input.style.border = "1px solid #ccc";
                }

            });

            if (!valid) {
                event.preventDefault();
                alert("Please fill in all required fields.");
            }

        });

    });


    // Password confirmation
    const password = document.querySelector("#password");
    const confirmPassword = document.querySelector("#confirm_password");

    if (password && confirmPassword) {

        confirmPassword.addEventListener("input", function () {

            if (password.value !== confirmPassword.value) {
                confirmPassword.style.border = "2px solid red";
            } else {
                confirmPassword.style.border = "2px solid green";
            }

        });

    }


    // Button click effect
    const buttons = document.querySelectorAll("button");

    buttons.forEach(function (button) {

        button.addEventListener("click", function () {
            console.log("Button clicked:", button.textContent);
        });

    });

});
