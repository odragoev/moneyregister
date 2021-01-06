let form = document.getElementById("category");
let edit = false;

// Edit button was clicked
function editClicked() {
    edit = true;
}
form.onsubmit = function() {
    // Check if form has categories to edit
    var element =  document.getElementById("ID");
    if (element == null && edit === true) {
        alert("no categories to edit");
        edit = false;
        return false;
    }
    return true;
};