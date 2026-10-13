
document.getElementById("officerLoginForm").addEventListener("submit", async function(event) {
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

        if (data.role !== "OFFICER") {
            throw new Error("Please use a Placement Officer account.");
        }

        if (!data.access_token) {
            throw new Error("Authentication token is missing.");
        }

        localStorage.setItem("user_id", data.user_id);
        localStorage.setItem("user_name", data.name);
        localStorage.setItem("user_email", data.email);
        localStorage.setItem("user_role", data.role);
        localStorage.setItem("access_token", data.access_token);

        window.location.href = "admin-dashboard.html";

    } catch (error) {
        console.error(error);
        message.textContent = error.message || "Unable to connect to server.";
    }
});
