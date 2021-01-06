let form = document.getElementById("index");
let edit = false;
let remove = false;

// Edit button was clicked
function editClicked() {
    edit = true;
}

// Remove button was clicked
function removeClicked() {
    remove = true;
}

form.onsubmit = function() {
    // Check if form has transactions to edit
    var element =  document.getElementById("ID");
    if (element == null && (edit === true || remove === true)) {
        alert("no transactions to alter");
        edit = false;
        remove = false;
        return false;
    }
    return true;
};