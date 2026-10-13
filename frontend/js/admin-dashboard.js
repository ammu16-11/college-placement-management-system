
const officerToken = localStorage.getItem("access_token");
const officerRole = localStorage.getItem("user_role");

if (!officerToken || officerRole !== "OFFICER") {
    window.location.replace("officer-login.html");
}

const API_URL = "http://127.0.0.1:5000";

async function officerFetch(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");

    if (!token || localStorage.getItem("user_role") !== "OFFICER") {
        localStorage.clear();
        window.location.replace("officer-login.html");
        throw new Error("Placement Officer login required.");
    }

    const headers = {
        ...(options.headers || {}),
        "Authorization": "Bearer " + token
    };

    if (options.body && !headers["Content-Type"]) {
        headers["Content-Type"] = "application/json";
    }

    const response = await fetch(API_URL + endpoint, {
        ...options,
        headers
    });

    if (response.status === 401 || response.status === 403) {
        throw new Error("Access denied. Please check your login and permissions.");
    }

    return response;
}




async function viewStudents() {
    try {
        const token = localStorage.getItem("access_token");

        if (!token) {
            alert("Please log in as a Placement Officer.");
            window.location.href = "officer-login.html";
            return;
        }

        const response = await fetch("http://127.0.0.1:5000/students", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const students = await response.json();

        if (!response.ok) {
            throw new Error(students.message || "Failed to fetch students.");
        }

        let content = "<div class='admin-box'><h2>Students</h2>";

        if (!Array.isArray(students) || students.length === 0) {
            content += "<p>No students found.</p>";
        } else {
            students.forEach(function(student) {
                content +=
                    "<div class='admin-card'>" +
                    "<h3>Student #" + student.student_id + "</h3>" +
                    "<p><strong>Student ID:</strong> " + student.student_id + "</p>" +
                    "<p><strong>User ID:</strong> " + student.user_id + "</p>" +
                    "<p><strong>Register Number:</strong> " + student.register_number + "</p>" +
                    "<p><strong>Department:</strong> " + student.department + "</p>" +
                    "<p><strong>CGPA:</strong> " + student.cgpa + "</p>" +
                    "<p><strong>Phone:</strong> " + student.phone + "</p>" +
                    "</div>";
            });
        }

        content += "</div>";
        document.getElementById("adminContent").innerHTML = content;

    } catch (error) {
        console.error("Students error:", error);
        alert(error.message || "Unable to load students.");
    }
}


async function viewCompanies() {
    try {
        const token = localStorage.getItem("access_token");

        if (!token) {
            alert("Please log in as a Placement Officer.");
            window.location.href = "officer-login.html";
            return;
        }

        const response = await fetch("http://127.0.0.1:5000/companies", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const companies = await response.json();

        if (!response.ok) {
            throw new Error(companies.message || "Failed to fetch companies.");
        }

        let content = "<div class='admin-box'><h2>Companies</h2>";

        if (!Array.isArray(companies) || companies.length === 0) {
            content += "<p>No companies found.</p>";
        } else {
            companies.forEach(function(company) {
                content +=
                    "<div class='admin-card'>" +
                    "<h3>" + company.company_name + "</h3>" +
                    "<p><strong>Company ID:</strong> " + company.company_id + "</p>" +
                    "</div>";
            });
        }

        content += "</div>";
        document.getElementById("adminContent").innerHTML = content;

    } catch (error) {
        console.error("Companies error:", error);
        alert(error.message || "Unable to load companies.");
    }
}




async function viewJobs() {
    try {
        const token = localStorage.getItem("access_token");

        if (!token) {
            alert("Please log in as a Placement Officer.");
            window.location.href = "officer-login.html";
            return;
        }

        const response = await fetch("http://127.0.0.1:5000/jobs", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const jobs = await response.json();

        if (!response.ok) {
            throw new Error(jobs.message || "Failed to fetch jobs.");
        }

        let content = "<div class='admin-box'><h2>Jobs</h2>";

        if (!Array.isArray(jobs) || jobs.length === 0) {
            content += "<p>No jobs found.</p>";
        } else {
            jobs.forEach(function(job) {
                content +=
                    "<div class='admin-card'>" +
                    "<h3>" + job.job_title + "</h3>" +
                    "<p><strong>Job ID:</strong> " + job.job_id + "</p>" +
                    "<p><strong>Company ID:</strong> " + job.company_id + "</p>" +
                    "<p><strong>Minimum CGPA:</strong> " + job.eligibility_cgpa + "</p>" +
                    "<p><strong>Salary:</strong> " + job.salary + " LPA</p>" +
                    "<p><strong>Location:</strong> " + job.location + "</p>" +
                    "<p><strong>Deadline:</strong> " + job.deadline + "</p>" +
                    "</div>";
            });
        }

        content += "</div>";
        document.getElementById("adminContent").innerHTML = content;

    } catch (error) {
        console.error("Jobs error:", error);
        alert(error.message || "Unable to load jobs.");
    }
}



async function viewApplications() {
    const content = document.getElementById("adminContent");
    content.innerHTML = "<p>Loading applications...</p>";

    try {
        const response = await officerFetch("/applications");

        if (!response.ok) {
            throw new Error("Unable to load applications.");
        }

        const applications = await response.json();

        if (!Array.isArray(applications) || applications.length === 0) {
            content.innerHTML = "<h2>Applications</h2><p>No applications found.</p>";
            return;
        }

        let html = `
            <h2>Application Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Application ID</th>
                        <th>Student ID</th>
                        <th>Job ID</th>
                        <th>Status</th>
                        <th>Applied At</th>
                    </tr>
                </thead>
                <tbody>
        `;

        applications.forEach(application => {
            html += `
                <tr>
                    <td>${application.application_id ?? ""}</td>
                    <td>${application.student_id ?? ""}</td>
                    <td>${application.job_id ?? ""}</td>
                    <td>${application.status ?? ""}</td>
                    <td>${application.applied_at ?? ""}</td>
                </tr>
            `;
        });

        html += "</tbody></table>";
        content.innerHTML = html;

    } catch (error) {
        console.error(error);
        content.innerHTML = `<p>${error.message || "Failed to load applications."}</p>`;
    }
}




async function viewInterviews() {
    const content = document.getElementById("adminContent");
    content.innerHTML = "<p>Loading interviews...</p>";

    try {
        const response = await officerFetch("/interviews");

        if (!response.ok) {
            throw new Error("Unable to load interviews.");
        }

        const interviews = await response.json();

        if (!Array.isArray(interviews) || interviews.length === 0) {
            content.innerHTML = "<h2>Interviews</h2><p>No interviews found.</p>";
            return;
        }

        let html = `
            <h2>Interview Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Interview ID</th>
                        <th>Application ID</th>
                        <th>Interview Date</th>
                        <th>Interview Time</th>
                        <th>Mode</th>
                        <th>Result</th>
                    </tr>
                </thead>
                <tbody>
        `;

        interviews.forEach(interview => {
            html += `
                <tr>
                    <td>${interview.interview_id ?? ""}</td>
                    <td>${interview.application_id ?? ""}</td>
                    <td>${interview.interview_date ?? ""}</td>
                    <td>${interview.interview_time ?? ""}</td>
                    <td>${interview.mode ?? ""}</td>
                    <td>${interview.result ?? ""}</td>
                </tr>
            `;
        });

        html += "</tbody></table>";
        content.innerHTML = html;

    } catch (error) {
        console.error(error);
        content.innerHTML = `<p>${error.message || "Failed to load interviews."}</p>`;
    }
}


async function viewPlacements() {
    const content = document.getElementById("adminContent");
    content.innerHTML = "<p>Loading placements...</p>";

    try {
        const response = await officerFetch("/placements");

        if (!response.ok) {
            throw new Error("Unable to load placements.");
        }

        const placements = await response.json();

        if (!Array.isArray(placements) || placements.length === 0) {
            content.innerHTML = "<h2>Placements</h2><p>No placements found.</p>";
            return;
        }

        let html = `
            <h2>Placement Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Placement ID</th>
                        <th>Student ID</th>
                        <th>Company ID</th>
                        <th>Job ID</th>
                        <th>Package (LPA)</th>
                        <th>Placement Date</th>
                    </tr>
                </thead>
                <tbody>
        `;

        placements.forEach(placement => {
            html += `
                <tr>
                    <td>${placement.placement_id ?? ""}</td>
                    <td>${placement.student_id ?? ""}</td>
                    <td>${placement.company_id ?? ""}</td>
                    <td>${placement.job_id ?? ""}</td>
                    <td>${placement.package_lpa ?? ""}</td>
                    <td>${placement.placement_date ?? ""}</td>
                </tr>
            `;
        });

        html += "</tbody></table>";
        content.innerHTML = html;

    } catch (error) {
        console.error(error);
        content.innerHTML = `<p>${error.message || "Failed to load placements."}</p>`;
    }
}