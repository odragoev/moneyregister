// Ensure date is valid
// https://stackoverflow.com/questions/18758772/how-do-i-validate-a-date-in-this-format-yyyy-mm-dd-using-jquery/18759013
function isValidDate(dateString) {
    var regEx = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateString.match(regEx)) {
        // Invalid format
        return false;
    }
    var d = new Date(dateString);
    if (Number.isNaN(d.getTime())) {
        // Invalid date
        return false;
    }
    return d.toISOString().slice(0,10) === dateString;
}

let form = document.getElementById("add_transaction");
form.onsubmit = function() {
    // Ensure date was submitted
    if (!form.date.value) {
        alert("must provide date");
        return false;
    }
    // Ensure date is valid
    if (isValidDate(form.date.value) === false) {
        alert("must provide valid date");
        return false;
    }
    // Ensure category was submitted
    if (!form.category.value) {
        alert("must provide category");
        return false;
    }
    // Ensure payee/payer was submitted
    if (!form.payee.value) {
        alert("must provide payee or payer");
        return false;
    }
    // Ensure EITHER payment or deposit was submitted
    if (!form.payment.value && !form.deposit.value) {
        alert("must provide payment OR deposit");
        return false;
    }
    if (form.payment.value && form.deposit.value) {
        alert("must provide payment OR deposit");
        return false;
    }
    return true;
};