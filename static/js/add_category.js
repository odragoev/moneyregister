let form = document.getElementById("add_category");
form.onsubmit = function() {
    // Ensure category was submitted
    if (!form.category.value) {
        alert("missing category");
        return false;
    }
    if (form.category.value !== "") {
        var pipeDelimited = form.pipeDelimited.value;
        var categories = pipeDelimited.split('\|');
        for (let category of categories) {
            // Ensure category name is unique
            if (form.category.value.toUpperCase() === category.toUpperCase()) {
                alert("must provide unique category name");
                return false;
            }
        }
    }
    return true;
};