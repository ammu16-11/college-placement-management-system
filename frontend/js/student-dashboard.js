
const API_BASE = "http://127.0.0.1:5000";

async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem("access_token");

    if (!token) {
        localStorage.clear();
        window.location.href = "student-login.html";
        throw new Error("Please log in again.");
    }

    const headers = {
        ...(options.headers || {}),
        Authorization: "Bearer " + token
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        localStorage.clear();
        window.location.href = "student-login.html";
        throw new Error("Your session has expired. Please log in again.");
    }

    return response;
}

async function getLoggedInStudent() {
    if (localStorage.getItem("user_role") !== "STUDENT") {
        throw new Error("Please log in with a student account.");
    }

    const response = await authenticatedFetch(`${API_BASE}/students`);

    if (!response.ok) {
        throw new Error("Unable to load your student profile.");
    }

    const student = await response.json();

    if (!student || !student.student_id) {
        throw new Error("Student profile not found.");
    }

    return student;
}

function showError(error) {
    console.error(error);
    alert(error.message || "Something went wrong. Please try again.");
}

const userName = localStorage.getItem("user_name");
const userRole = localStorage.getItem("user_role");

if (!userName || userRole !== "STUDENT") {
    window.location.href = "student-login.html";
} else {
    const welcomeMessage = document.getElementById("welcomeMessage");

    if (welcomeMessage) {
        welcomeMessage.textContent = "Welcome, " + userName;
    }
}

async function viewProfile() {
    try {
        const student = await getLoggedInStudent();

        document.getElementById("dashboardContent").innerHTML =
            "<div class='profile-box'>" +
            "<h2>My Profile</h2>" +
            "<p><strong>Register Number:</strong> " + (student.register_number || "Not provided") + "</p>" +
            "<p><strong>Department:</strong> " + (student.department || "Not provided") + "</p>" +
            "<p><strong>CGPA:</strong> " + (student.cgpa ?? "Not provided") + "</p>" +
            "<p><strong>Phone:</strong> " + (student.phone || "Not provided") + "</p>" +
            "<p><strong>Resume:</strong> " +
                (student.resume_url ? "Uploaded" : "Not uploaded") + "</p>" +
                "<form id='resumeUploadForm' enctype='multipart/form-data'>" +
                "<label for='resumeFile'>Upload resume (PDF, maximum 5 MB):</label><br>" +
                "<input type='file' id='resumeFile' name='resume' accept='.pdf,application/pdf' required>" +
                "<button type='submit'>Upload Resume</button>" +
                "</form>" +
                (student.resume_url
                    ? "<button type='button' onclick='downloadResume()'>Download My Resume</button>"
                    : "") +
                "<p id='resumeMessage' aria-live='polite'></p>" +
            "</div>";
    } catch (error) {
        showError(error);
    }
}

async function viewJobs() {
    try {
        const response = await fetch(`${API_BASE}/jobs`);

        if (!response.ok) {
            throw new Error("Unable to load available jobs.");
        }

        const jobs = await response.json();

        if (!Array.isArray(jobs) || jobs.length === 0) {
            document.getElementById("dashboardContent").innerHTML =
                "<h2>Available Jobs</h2><p>No jobs available.</p>";
            return;
        }

        let jobDetails = "";

        jobs.forEach(function(job) {
            jobDetails +=
                "<div class='job-card'>" +
                "<h3>" + job.job_title + "</h3>" +
                "<p><strong>Job ID:</strong> " + job.job_id + "</p>" +
                "<p><strong>Minimum CGPA:</strong> " + job.eligibility_cgpa + "</p>" +
                "<p><strong>Salary:</strong> " + job.salary + " LPA</p>" +
                "<p><strong>Location:</strong> " + job.location + "</p>" +
                "<p><strong>Deadline:</strong> " + job.deadline + "</p>" +
                "<button onclick='applyForJob(" + Number(job.job_id) + ")'>Apply Now</button>" +
                "</div>";
        });

        document.getElementById("dashboardContent").innerHTML =
            "<div class='job-box'><h2>Available Jobs</h2>" +
            jobDetails + "</div>";
    } catch (error) {
        showError(error);
    }
}

async function applyForJob(jobId) {
    try {
        const response = await authenticatedFetch(`${API_BASE}/applications`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                job_id: Number(jobId)
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || "Unable to submit application.");
        }

        alert(data.message || "Application submitted successfully!");
        await viewApplications();
    } catch (error) {
        showError(error);
    }
}

async function viewApplications() {
    try {
        const response = await authenticatedFetch(`${API_BASE}/applications`);

        if (!response.ok) {
            throw new Error("Unable to load applications.");
        }

        const applications = await response.json();
        let details = "";

        applications.forEach(function(application) {
            details +=
                "<div class='application-card'>" +
                "<h3>Application #" + application.application_id + "</h3>" +
                "<p><strong>Job ID:</strong> " + application.job_id + "</p>" +
                "<p><strong>Status:</strong> " + application.status + "</p>" +
                "<p><strong>Applied At:</strong> " + (application.applied_at || "Not available") + "</p>" +
                "</div>";
        });

        document.getElementById("dashboardContent").innerHTML =
            "<div class='application-box'><h2>My Applications</h2>" +
            (details || "<p>You haven't applied for any jobs yet. Visit Available Jobs to get started.</p>")
            "</div>";
    } catch (error) {
        showError(error);
    }
}

async function viewInterviews() {
    try {
        const response = await authenticatedFetch(`${API_BASE}/interviews`);

        if (!response.ok) {
            throw new Error("Unable to load interviews.");
        }

        const interviews = await response.json();
        let details = "";

        interviews.forEach(function(interview) {
            details +=
                "<div class='interview-card'>" +
                "<h3>Interview #" + interview.interview_id + "</h3>" +
                "<p><strong>Application ID:</strong> " + interview.application_id + "</p>" +
                "<p><strong>Date:</strong> " + interview.interview_date + "</p>" +
                "<p><strong>Time:</strong> " + interview.interview_time + "</p>" +
                "<p><strong>Mode:</strong> " + (interview.mode || "Not specified") + "</p>" +
                "<p><strong>Result:</strong> " + (interview.result || "Pending") + "</p>" +
                "</div>";
        });

        document.getElementById("dashboardContent").innerHTML =
            "<div class='interview-box'><h2>My Interviews</h2>" +
            (details || "<p>No interviews scheduled yet. Apply for a job to get started.</p>")
            "</div>";
    } catch (error) {
        showError(error);
    }
}

async function viewPlacement() {
    try {
        const response = await authenticatedFetch(`${API_BASE}/placements`);

        if (!response.ok) {
            throw new Error("Unable to load placement records.");
        }

        const placements = await response.json();
        let details = "";

        placements.forEach(function(placement) {
            details +=
                "<div class='placement-card'>" +
                "<h3>Placement #" + placement.placement_id + "</h3>" +
                "<p><strong>Company ID:</strong> " + placement.company_id + "</p>" +
                "<p><strong>Job ID:</strong> " + placement.job_id + "</p>" +
                "<p><strong>Package:</strong> " + (placement.package_lpa ?? "Not available") + " LPA</p>" +
                "<p><strong>Placement Date:</strong> " + (placement.placement_date || "Not available") + "</p>" +
                "</div>";
        });

        document.getElementById("dashboardContent").innerHTML =
            "<div class='placement-box'><h2>My Placement</h2>" +
            (details || "<p>No placement results available yet.</p>")
            "</div>";
    } catch (error) {
        showError(error);
    }
}

async function logout() {
    const token = localStorage.getItem("access_token");

    try {
        if (token) {
            await fetch("http://127.0.0.1:5000/logout", {
                method: "POST",
                headers: {
                    "Authorization": "Bearer " + token
                }
            });
        }
    } catch (error) {
        console.error("Backend logout request failed:", error);
    } finally {
        localStorage.clear();
        window.location.href = "student-login.html";
    }
}

async function uploadResume(event) {
    event.preventDefault();

    const fileInput = document.getElementById("resumeFile");
    const message = document.getElementById("resumeMessage");
    const file = fileInput.files[0];

    if (!file) {
        message.textContent = "Please select a PDF file.";
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        message.textContent = "The resume must be 5 MB or smaller.";
        return;
    }

    if (
        file.type !== "application/pdf" &&
        !file.name.toLowerCase().endsWith(".pdf")
    ) {
        message.textContent = "Only PDF resumes are allowed.";
        return;
    }

    const formData = new FormData();
    formData.append("resume", file);

    try {
        message.textContent = "Uploading resume...";

        const response = await authenticatedFetch(
            `${API_BASE}/student/resume`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();
        console.log("Resume upload response:", data);
        console.log("Resume upload status:", response.status);

        if (!response.ok) {
            throw new Error(data.message || "Resume upload failed.");
        }

        await viewProfile();

        const updatedMessage = document.getElementById("resumeMessage");

        if (updatedMessage) {
            updatedMessage.textContent = "Resume uploaded successfully.";
        }
    } catch (error) {
        message.textContent = error.message || "Unable to upload resume.";
    }
}

async function downloadResume() {
    const message = document.getElementById("resumeMessage");

    try {
        message.textContent = "Preparing download...";

        const response = await authenticatedFetch(
            `${API_BASE}/student/resume`
        );

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || "Unable to download resume.");
        }

        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = downloadUrl;
        link.download = "my_resume.pdf";
        document.body.appendChild(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(downloadUrl);
        message.textContent = "Resume download started.";
    } catch (error) {
        message.textContent = error.message || "Unable to download resume.";
    }
}

document.addEventListener("submit", function(event) {
    if (event.target && event.target.id === "resumeUploadForm") {
        uploadResume(event);
    }
});