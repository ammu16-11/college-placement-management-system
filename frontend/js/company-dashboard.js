async function viewCompanyProfile() {
try {
const response = await fetch("http://3.106.120.107:5000/companies");
const companies = await response.json();


    const company = companies.find(company => company.company_id === 1);

    if (company) {
        document.getElementById("companyContent").innerHTML =
            "<div class='company-profile-box'>" +
            "<h2>Company Profile</h2>" +
            "<p><strong>Company ID:</strong> " + company.company_id + "</p>" +
            "<p><strong>Company Name:</strong> " + company.company_name + "</p>" +
            "<p><strong>User ID:</strong> " + company.user_id + "</p>" +
            "</div>";
    } else {
        alert("Company profile not found.");
    }

} catch (error) {
    alert("Unable to load company profile.");
}


}

function postJob() {
document.getElementById("companyContent").innerHTML =
"<div class='company-form-box'>" +
"<h2>Post a New Job</h2>" +
"<form id='jobForm'>" +


    "<input type='text' id='jobTitle' placeholder='Job Title' required>" +

    "<input type='number' id='eligibilityCgpa' placeholder='Minimum CGPA' step='0.1' required>" +

    "<input type='number' id='salaryLpa' placeholder='Salary (LPA)' step='0.1' required>" +

    "<input type='text' id='jobLocation' placeholder='Location' required>" +

    "<input type='date' id='jobDeadline' required>" +

    "<button type='submit'>Post Job</button>" +

    "</form>" +
    "</div>";

document.getElementById("jobForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const jobData = {
        company_id: 1,
        title: document.getElementById("jobTitle").value,
        eligibility_cgpa: parseFloat(document.getElementById("eligibilityCgpa").value),
        salary_lpa: parseFloat(document.getElementById("salaryLpa").value),
        location: document.getElementById("jobLocation").value,
        deadline: document.getElementById("jobDeadline").value
    };

    try {
        const response = await fetch("http://3.106.120.107:5000/jobs", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(jobData)
        });

        const data = await response.json();

        if (response.ok) {
            alert("Job posted successfully!");
            document.getElementById("jobForm").reset();
        } else {
            alert(data.message || "Unable to post job.");
        }

    } catch (error) {
        alert("Unable to connect to server.");
    }
});


}

async function viewCompanyJobs() {
try {
const response = await fetch("http://3.106.120.107:5000/jobs");
const jobs = await response.json();


    const companyJobs = jobs.filter(job => job.company_id === 1);

    if (companyJobs.length === 0) {
        alert("No jobs posted by this company.");
        return;
    }

    let jobDetails = "";

    companyJobs.forEach(function(job) {
        jobDetails +=
            "<div class='company-job-card'>" +
            "<h3>" + job.title + "</h3>" +
            "<p><strong>Job ID:</strong> " + job.job_id + "</p>" +
            "<p><strong>Minimum CGPA:</strong> " + job.eligibility_cgpa + "</p>" +
            "<p><strong>Salary:</strong> " + job.salary_lpa + " LPA</p>" +
            "<p><strong>Location:</strong> " + job.location + "</p>" +
            "<p><strong>Deadline:</strong> " + job.deadline + "</p>" +
            "</div>";
    });

    document.getElementById("companyContent").innerHTML =
        "<div class='company-jobs-box'>" +
        "<h2>My Posted Jobs</h2>" +
        jobDetails +
        "</div>";

} catch (error) {
    alert("Unable to load company jobs.");
}


}

async function viewCompanyApplications() {
    try {
        const applicationsResponse = await fetch("http://3.106.120.107:5000/applications");
        const applications = await applicationsResponse.json();

        if (applications.length === 0) {
            document.getElementById("companyContent").innerHTML =
                "<div class='company-applications-box'>" +
                "<h2>Student Applications</h2>" +
                "<p>No applications found.</p>" +
                "</div>";
            return;
        }

        const jobsResponse = await fetch("http://3.106.120.107:5000/jobs");
        const jobs = await jobsResponse.json();

        const companyJobIds = jobs
            .filter(job => job.company_id === 1)
            .map(job => job.job_id);

        const companyApplications = applications.filter(
            application => companyJobIds.includes(application.job_id)
        );

        if (companyApplications.length === 0) {
            document.getElementById("companyContent").innerHTML =
                "<div class='company-applications-box'>" +
                "<h2>Student Applications</h2>" +
                "<p>No applications found for your jobs.</p>" +
                "</div>";
            return;
        }

        let applicationDetails = "";

        companyApplications.forEach(function(application) {
            applicationDetails +=
                "<div class='company-application-card'>" +
                "<h3>Application #" + application.application_id + "</h3>" +
                "<p><strong>Student ID:</strong> " + application.student_id + "</p>" +
                "<p><strong>Job ID:</strong> " + application.job_id + "</p>" +
                "<p><strong>Status:</strong> <span class='company-status'>" + application.status + "</span></p>" +
                "<p><strong>Applied At:</strong> " + application.applied_at + "</p>" +

                "<div class='application-actions'>" +

                "<button onclick='updateApplicationStatus(" +
                application.application_id +
                ", \"SHORTLISTED\")'>" +
                "Shortlist" +
                "</button>" +

                "<button onclick='updateApplicationStatus(" +
                application.application_id +
                ", \"REJECTED\")'>" +
                "Reject" +
                "</button>" +

                "</div>" +

                "</div>";
        });

        document.getElementById("companyContent").innerHTML =
            "<div class='company-applications-box'>" +
            "<h2>Student Applications</h2>" +
            applicationDetails +
            "</div>";

    } catch (error) {
        console.error(error);
        alert("Unable to load applications.");
    }
}


async function updateApplicationStatus(applicationId, newStatus) {
    try {
        const response = await fetch(
            "http://3.106.120.107:5000/applications/" + applicationId,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        const data = await response.json();

        if (response.ok) {
            alert("Application status updated successfully!");
            viewCompanyApplications();
        } else {
            alert(data.message || "Unable to update application status.");
        }

    } catch (error) {
        console.error(error);
        alert("Unable to connect to server.");
    }
}

async function viewCompanyInterviews() {
try {
const response = await fetch("http://3.106.120.107:5000/interviews");
const interviews = await response.json();


    if (interviews.length === 0) {
        alert("No interviews found.");
        return;
    }

    let interviewDetails = "";

    interviews.forEach(function(interview) {
        interviewDetails +=
            "<div class='company-interview-card'>" +
            "<h3>Interview #" + interview.interview_id + "</h3>" +
            "<p><strong>Application ID:</strong> " + interview.application_id + "</p>" +
            "<p><strong>Date:</strong> " + interview.interview_date + "</p>" +
            "<p><strong>Time:</strong> " + interview.interview_time + "</p>" +
            "<p><strong>Mode:</strong> " + interview.mode + "</p>" +
            "<p><strong>Result:</strong> <span class='company-interview-result'>" + interview.result + "</span></p>" +
            "</div>";
    });

    document.getElementById("companyContent").innerHTML =
        "<div class='company-interviews-box'>" +
        "<h2>Student Interviews</h2>" +
        interviewDetails +
        "</div>";

} catch (error) {
    alert("Unable to load interviews.");
}

}

