document.addEventListener("DOMContentLoaded", function () {
    var form = document.querySelector("form");

    form.addEventListener("submit", function (event) {
        var password1 = document.getElementById("pswd1").value;
        var password2 = document.getElementById("pswd2").value;

        if (password1 !== password2) {
            alert("Passwords do not match. Please try again.");
            event.preventDefault(); // Prevent the form from submitting
        }
    });
});
