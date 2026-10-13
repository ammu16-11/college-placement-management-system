document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");

    message.textContent = "Logging in...";

    try {
        const response = await fetch("http://127.0.0.1:5000/login", {
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

        if (!response.ok || data.status !== "success") {
            throw new Error(data.message || "Login failed.");
        }

        if (data.role !== "STUDENT") {
            throw new Error("Please use a student account to log in here.");
        }

        if (!data.access_token) {
            throw new Error("Authentication token is missing. Please try again later.");
        }

        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("user_name", data.name);
        localStorage.setItem("user_email", data.email);
        localStorage.setItem("user_role", data.role);
        localStorage.setItem("access_token", data.access_token);

        window.location.href = "student-dashboard.html";

    } catch (error) {
        message.textContent = error.message || "Unable to connect to server.";
    }
});