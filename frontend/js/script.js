function selectRole(role) {

    if (role === "student") {
        window.location.href = "student-login.html";
    }

    else if (role === "company") {
        window.location.href = "company-login.html";
    }

    else if (role === "admin") {
        window.location.href = "admin-dashboard.html";
    }

}

