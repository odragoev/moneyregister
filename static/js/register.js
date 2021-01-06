let form = document.getElementById("register");
form.onsubmit = function() {
    // Ensure username was submitted
    if (!form.username.value) {
        alert("must provide username");
        return false;
    }
    // Ensure username is unique
    if (form.username.value !== "") {
        var pipeDelimited = form.pipeDelimited.value;
        var usernames = pipeDelimited.split('\|');
        for (let username of usernames) {
            if (form.username.value === username) {
                alert("username taken");
                return false;
            }
        }
    }
    // Ensure password was submitted
    if (!form.password.value) {
        alert("must provide password");
        return false;
    }
    // Ensure confirmation was submitted
    if (!form.confirmation.value) {
        alert("must provide password confirmation");
        return false;
    }
    // Ensure password and confirmation match
    if (form.password.value !== form.confirmation.value){
        alert("password and confirmation do not match");
        return false;
    }
    return true;
};