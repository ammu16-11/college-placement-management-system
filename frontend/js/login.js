
document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");

    try {
        const response = await fetch("http://3.106.120.107:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (data.status === "success") {
            window.location.href = "student-dashboard.html";
        } else {
            message.innerHTML = data.message;
        }

    } catch (error) {
        console.error(error);
        message.innerHTML = "Unable to connect to server.";
    }
});

