
const API_URL = "http://3.106.120.107:5000";

function getAuthHeaders() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("Your login session is missing. Please log in again.");
        window.location.href = "company-login.html";
        throw new Error("Authentication token missing");
    }

    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

async function getMyCompany() {
    const response = await fetch(`${API_URL}/companies`);
    const companies = await response.json();

    if (!response.ok || !Array.isArray(companies)) {
        throw new Error("Unable to retrieve company details");
    }

    const userId = Number(localStorage.getItem("user_id"));
    const company = companies.find(item => Number(item.user_id) === userId);

    if (!company) {
        throw new Error("Company profile not found for this account");
    }

    return company;
}

async function viewCompanyProfile() {
    try {
        const company = await getMyCompany();

        document.getElementById("companyContent").innerHTML =
            "<div class='company-profile-box'>" +
            "<h2>Company Profile</h2>" +
            "<p><strong>Company ID:</strong> " + company.company_id + "</p>" +
            "<p><strong>Company Name:</strong> " + company.company_name + "</p>" +
            "<p><strong>User ID:</strong> " + company.user_id + "</p>" +
            "</div>";
    } catch (error) {
        console.error(error);
        alert(error.message || "Unable to load company profile.");
    }
}

function postJob() {
    document.getElementById("companyContent").innerHTML =
        "<div class='company-form-box'>" +
        "<h2>Post a New Job</h2>" +
        "<form id='jobForm'>" +
        "<input type='text' id='jobTitle' placeholder='Job Title' required>" +
        "<input type='number' id='eligibilityCgpa' placeholder='Minimum CGPA' min='0' max='10' step='0.1' required>" +
        "<input type='number' id='salaryLpa' placeholder='Salary (LPA)' min='0.1' step='0.1' required>" +
        "<input type='text' id='jobLocation' placeholder='Location' required>" +
        "<input type='date' id='jobDeadline' required>" +
        "<button type='submit'>Post Job</button>" +
        "</form>" +
        "</div>";

    document.getElementById("jobForm").addEventListener("submit", async function(event) {
        event.preventDefault();

        try {
            const company = await getMyCompany();

            const jobData = {
                company_id: company.company_id,
                title: document.getElementById("jobTitle").value.trim(),
                eligibility_cgpa: Number(document.getElementById("eligibilityCgpa").value),
                salary_lpa: Number(document.getElementById("salaryLpa").value),
                location: document.getElementById("jobLocation").value.trim(),
                deadline: document.getElementById("jobDeadline").value
            };

            const response = await fetch(`${API_URL}/jobs`, {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify(jobData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || "Unable to post job.");
            }

            alert("Job posted successfully!");
            document.getElementById("jobForm").reset();
        } catch (error) {
            console.error(error);

            if (error.message !== "Authentication token missing") {
                alert(error.message || "Unable to connect to server.");
            }
        }
    });
}

async function viewCompanyJobs() {
    try {
        const company = await getMyCompany();
        const response = await fetch(`${API_URL}/jobs`);
        const jobs = await response.json();

        if (!response.ok || !Array.isArray(jobs)) {
            throw new Error("Unable to retrieve jobs");
        }

        const companyJobs = jobs.filter(
            job => Number(job.company_id) === Number(company.company_id)
        );

        let jobDetails = "";

        companyJobs.forEach(function(job) {
            jobDetails +=
                "<div class='company-job-card'>" +
                "<h3>" + (job.job_title || "Untitled job") + "</h3>" +
                "<p><strong>Job ID:</strong> " + job.job_id + "</p>" +
                "<p><strong>Minimum CGPA:</strong> " + job.eligibility_cgpa + "</p>" +
                "<p><strong>Salary:</strong> " + job.salary + " LPA</p>" +
                "<p><strong>Location:</strong> " + job.location + "</p>" +
                "<p><strong>Deadline:</strong> " + job.deadline + "</p>" +
                "</div>";
        });

        document.getElementById("companyContent").innerHTML =
            "<div class='company-jobs-box'>" +
            "<h2>My Posted Jobs</h2>" +
            (jobDetails || "<p>No jobs posted by this company.</p>") +
            "</div>";
    } catch (error) {
        console.error(error);
        alert(error.message || "Unable to load company jobs.");
    }
}

async function viewCompanyApplications() {
    try {
        const response = await fetch(`${API_URL}/applications`, {
            headers: getAuthHeaders()
        });

        const applications = await response.json();

        if (!response.ok) {
            throw new Error(applications.message || "Unable to load applications.");
        }

        if (!Array.isArray(applications)) {
            throw new Error("Unexpected applications response.");
        }

        let applicationDetails = "";

        applications.forEach(function(application) {
            const status = String(application.status || "APPLIED").toUpperCase();
            const canUpdate = status === "APPLIED" || status === "SHORTLISTED";

            applicationDetails +=
                "<div class='company-application-card'>" +
                "<h3>Application #" + application.application_id + "</h3>" +
                "<p><strong>Student ID:</strong> " + application.student_id + "</p>" +
                "<p><strong>Job ID:</strong> " + application.job_id + "</p>" +
                "<p><strong>Status:</strong> <span class='company-status'>" + status + "</span></p>" +
                "<p><strong>Applied At:</strong> " + (application.applied_at || "N/A") + "</p>" +
                (canUpdate
                    ? "<button type='button' class='shortlist-application-btn' data-id='" + application.application_id + "'>Shortlist</button> " +
                      "<button type='button' class='reject-application-btn' data-id='" + application.application_id + "'>Reject</button>"
                    : "") +
                "</div>";
        });

        document.getElementById("companyContent").innerHTML =
            "<div class='company-applications-box'>" +
            "<h2>Student Applications</h2>" +
            (applicationDetails || "<p>No applications found for your jobs.</p>") +
            "</div>";

        document.querySelectorAll(".shortlist-application-btn").forEach(function(button) {
            button.addEventListener("click", function() {
                updateCompanyApplicationStatus(button.dataset.id, "SHORTLISTED");
            });
        });

        document.querySelectorAll(".reject-application-btn").forEach(function(button) {
            button.addEventListener("click", function() {
                updateCompanyApplicationStatus(button.dataset.id, "REJECTED");
            });
        });

    } catch (error) {
        console.error(error);

        if (error.message !== "Authentication token missing") {
            alert(error.message || "Unable to load applications.");
        }
    }
}

async function updateCompanyApplicationStatus(applicationId, status) {
    const action = status === "SHORTLISTED" ? "shortlist" : "reject";

    if (!confirm("Are you sure you want to " + action + " this application?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/applications/${applicationId}`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: JSON.stringify({ status: status })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Unable to update application status.");
        }

        alert(data.message || "Application status updated successfully.");
        await viewCompanyApplications();

    } catch (error) {
        console.error(error);

        if (error.message !== "Authentication token missing") {
            alert(error.message || "Unable to update application status.");
        }
    }
}


async function viewCompanyInterviews() {
    try {
        const response = await fetch(`${API_URL}/interviews`, {
            headers: getAuthHeaders()
        });

        const interviews = await response.json();

        if (!response.ok) {
            throw new Error(interviews.message || "Unable to load interviews.");
        }

        if (!Array.isArray(interviews)) {
            throw new Error("Unexpected interviews response.");
        }

        let interviewDetails = "";

        interviews.forEach(function(interview) {
            interviewDetails +=
                "<div class='company-interview-card'>" +
                "<h3>Interview #" + interview.interview_id + "</h3>" +
                "<p><strong>Application ID:</strong> " + interview.application_id + "</p>" +
                "<p><strong>Date:</strong> " + (interview.interview_date || "N/A") + "</p>" +
                "<p><strong>Time:</strong> " + (interview.interview_time || "N/A") + "</p>" +
                "<p><strong>Mode:</strong> " + (interview.mode || "N/A") + "</p>" +
                "<p><strong>Result:</strong> <span class='company-interview-result'>" + (interview.result || "PENDING") + "</span></p>" +
                "</div>";
        });

        document.getElementById("companyContent").innerHTML =
            "<div class='company-interviews-box'>" +
            "<h2>Student Interviews</h2>" +
            (interviewDetails || "<p>No interviews found for your jobs.</p>") +
            "</div>";
    } catch (error) {
        console.error(error);

        if (error.message !== "Authentication token missing") {
            alert(error.message || "Unable to load interviews.");
        }
    }
}
