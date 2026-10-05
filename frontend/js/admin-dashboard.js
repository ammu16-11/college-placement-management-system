
async function viewStudents() {
    try {
        const response = await fetch("http://127.0.0.1:5000/students");

        const students = await response.json();

        let content = "<div class='admin-box'><h2>Students</h2>";

        if (students.length === 0) {

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

        console.error(error);

        alert("Unable to load students.");

    }
}



async function viewCompanies() {
    try {
        const response = await fetch("http://127.0.0.1:5000/companies");
        const companies = await response.json();

        let content = "<div class='admin-box'><h2>Companies</h2>";

        if (companies.length === 0) {
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
        console.error(error);
        alert("Unable to load companies.");
    }
}


async function viewJobs() {
    try {
        const response = await fetch("http://127.0.0.1:5000/jobs");
        const jobs = await response.json();

        let content = "<div class='admin-box'><h2>Jobs</h2>";

        if (jobs.length === 0) {
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
        console.error(error);
        alert("Unable to load jobs.");
    }
}


async function viewApplications() {
    try {
        const response = await fetch("http://127.0.0.1:5000/applications");
        const applications = await response.json();

        let content = "<div class='admin-box'><h2>Applications</h2>";

        if (applications.length === 0) {
            content += "<p>No applications found.</p>";
        } else {
            applications.forEach(function(application) {
                content +=
                    "<div class='admin-card'>" +
                    "<h3>Application #" + application.application_id + "</h3>" +
                    "<p><strong>Student ID:</strong> " + application.student_id + "</p>" +
                    "<p><strong>Job ID:</strong> " + application.job_id + "</p>" +
                    "<p><strong>Status:</strong> " + application.status + "</p>" +
                    "<p><strong>Applied At:</strong> " + application.applied_at + "</p>" +
                    "</div>";
            });
        }

        content += "</div>";

        document.getElementById("adminContent").innerHTML = content;

    } catch (error) {
        console.error(error);
        alert("Unable to load applications.");
    }
}


async function viewInterviews() {
    try {
        const response = await fetch("http://127.0.0.1:5000/interviews");
        const interviews = await response.json();

        let content = "<div class='admin-box'><h2>Interviews</h2>";

        if (interviews.length === 0) {
            content += "<p>No interviews found.</p>";
        } else {
            interviews.forEach(function(interview) {
                content +=
                    "<div class='admin-card'>" +
                    "<h3>Interview #" + interview.interview_id + "</h3>" +
                    "<p><strong>Application ID:</strong> " + interview.application_id + "</p>" +
                    "<p><strong>Date:</strong> " + interview.interview_date + "</p>" +
                    "<p><strong>Time:</strong> " + interview.interview_time + "</p>" +
                    "<p><strong>Mode:</strong> " + interview.mode + "</p>" +
                    "<p><strong>Result:</strong> " + interview.result + "</p>" +
                    "</div>";
            });
        }

        content += "</div>";

        document.getElementById("adminContent").innerHTML = content;

    } catch (error) {
        console.error(error);
        alert("Unable to load interviews.");
    }
}

async function viewPlacements() {
    try {
        const response = await fetch("http://127.0.0.1:5000/placements");
        const placements = await response.json();

        let content = "<div class='admin-box'><h2>Placements</h2>";

        if (placements.length === 0) {
            content += "<p>No placements found.</p>";
        } else {
            placements.forEach(function(placement) {
                content +=
                    "<div class='admin-card'>" +
                    "<h3>Placement #" + placement.placement_id + "</h3>" +
                    "<p><strong>Student ID:</strong> " + placement.student_id + "</p>" +
                    "<p><strong>Company ID:</strong> " + placement.company_id + "</p>" +
                    "<p><strong>Job ID:</strong> " + placement.job_id + "</p>" +
                    "<p><strong>Package:</strong> " + placement.package_lpa + " LPA</p>" +
                    "<p><strong>Placement Date:</strong> " + placement.placement_date + "</p>" +
                    "</div>";
            });
        }

        content += "</div>";

        document.getElementById("adminContent").innerHTML = content;

    } catch (error) {
        console.error(error);
        alert("Unable to load placements.");
    }
}
