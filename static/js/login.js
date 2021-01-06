function login(event) {
    var username = document.getElementById("username");
    var password = document.getElementById("password");
    // Ensure username was submitted
    if (username.value === "") {
        alert("must provide username");
        event.preventDefault();
        event.stopPropagation();
        return;
    }
    // Ensure password was submitted
    if (password.value === "") {
        alert("must provide password");
        event.preventDefault();
        event.stopPropagation();
        return;
    }
    let data = {
        "username": username.value,
        "password": password.value
    };
    // Ensure username and password are valid
    $.ajax({
        type: "POST",
        url: "/login",
        data: JSON.stringify(data),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(result) {
            if (result["valid"] === "true") {
                window.location="/";
            } else {
                alert("invalid username and/or password");
            }
        }
    });
}

var button = document.getElementById("login_button");
button.addEventListener("click", function(event) {
    login(event);
});

button.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        login(event);
    }
});