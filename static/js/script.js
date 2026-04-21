// Form validation
function validateForm(formType) {

    if (formType === "login") {
        let email = document.getElementById("email").value;
        let password = document.getElementById("password").value;

        if (email === "" || password === "") {
            alert("All fields are required!");
            return false;
        }
    }

    if (formType === "create") {
        let name = document.getElementById("name").value;
        let email = document.getElementById("email").value;

        if (name === "" || email === "") {
            alert("Please fill all fields!");
            return false;
        }
    }

    if (formType === "email") {
        let to = document.getElementById("email").value;
        let subject = document.getElementById("subject").value;
        let message = document.getElementById("message").value;

        if (to === "" || subject === "" || message === "") {
            alert("All fields are required!");
            return false;
        }
    }

    return true;
}


// Show success message dynamically
function showMessage(type, msg) {
    let div = document.createElement("div");
    div.className = type;
    div.innerText = msg;

    document.body.appendChild(div);

    setTimeout(() => {
        div.remove();
    }, 3000);
}