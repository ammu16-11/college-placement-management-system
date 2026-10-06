
async function viewProfile() {
    try {
        const response = await fetch("http://3.106.120.107:5000/students");
        const students = await response.json();

        const student = students.find(student => student.student_id === 1);

        if (student) {
            document.getElementById("dashboardContent").innerHTML =
                "<div class='profile-box'>" +
                "<h2>My Profile</h2>" +
                "<p><strong>Register Number:</strong> " + student.register_number + "</p>" +
                "<p><strong>Department:</strong> " + student.department + "</p>" +
                "<p><strong>CGPA:</strong> " + student.cgpa + "</p>" +
                "<p><strong>Phone:</strong> " + student.phone + "</p>" +
                "<p><strong>Resume:</strong> " + student.resume_url + "</p>" +
                "</div>";
        } else {
            alert("Student profile not found.");
        }

    } catch (error) {
        alert("Unable to load student profile.");
    }
}

async function viewJobs() {
    try {
        const response = await fetch("http://3.106.120.107:5000/jobs");
        const jobs = await response.json();

        if (jobs.length === 0) {
            alert("No jobs available.");
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
                "<button onclick='applyForJob(" + job.job_id + ")'>Apply Now</button>" +
                "</div>";
        });

        document.getElementById("dashboardContent").innerHTML =
            "<div class='job-box'>" +
            "<h2>Available Jobs</h2>" +
            jobDetails +
            "</div>";

    } catch (error) {
        alert("Unable to load available jobs.");
    }
}


async function applyForJob(jobId) {
    try {
        const response = await fetch("http://3.106.120.107:5000/applications", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                student_id: 1,
                job_id: jobId
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert("Application submitted successfully!");
        } else {
            alert(data.message || "Unable to submit application.");
        }

    } catch (error) {
        alert("Unable to connect to server.");
    }
}

async function viewApplications() {
    try {
        const response = await fetch("http://3.106.120.107:5000/applications");
        const applications = await response.json();

        const studentApplications = applications.filter(
            application => application.student_id === 1
        );

        if (studentApplications.length === 0) {
            alert("No applications found.");
            return;
        }

        let applicationDetails = "My Applications\n\n";

        studentApplications.forEach(function(application) {
            applicationDetails +=
                "<div class='application-card'>" +
                "<h3>Application #" + application.application_id + "</h3>" +
                "<p><strong>Job ID:</strong> " + application.job_id + "</p>" +
                "<p><strong>Status:</strong> <span class='status'>" + application.status + "</span></p>" +
                "<p><strong>Applied At:</strong> " + application.applied_at + "</p>" +
                "</div>";
        });
        document.getElementById("dashboardContent").innerHTML =
            "<div class='application-box'>" +
            "<h2>My Applications</h2>" +
            applicationDetails + 
            "</div>";
        
    } catch (error) {
        alert("Unable to load applications.");
    }
}
async function viewInterviews() {
    try {
        const response = await fetch("http://3.106.120.107:5000/interviews");
        const interviews = await response.json();

        const studentInterviews = interviews;

        if (studentInterviews.length === 0) {
            alert("No interviews found.");
            return;
        }

        let interviewDetails = "My Interviews\n\n";

        studentInterviews.forEach(function(interview) {
            interviewDetails +=
                "<div class='interview-card'>" +
                "<h3>Interview #" + interview.interview_id + "</h3>" +
                "<p><strong>Application ID:</strong> " + interview.application_id + "</p>" +
                "<p><strong>Date:</strong> " + interview.interview_date + "</p>" +
                "<p><strong>Time:</strong> " + interview.interview_time + "</p>" +
                "<p><strong>Mode:</strong> " + interview.mode + "</p>" +
                "<p><strong>Result:</strong> <span class='interview-result'>" + interview.result + "</span></p>" +
                "</div>";
        });
        document.getElementById("dashboardContent").innerHTML =
            "<div class='interview-box'>" +
            "<h2>My Interviews</h2>" +
            interviewDetails + 
            "</div>";

    } catch (error) {
        alert("Unable to load interviews.");
    }
}

async function viewPlacement() {
    try {
        const response = await fetch("http://3.106.120.107:5000/placements");
        const placements = await response.json();

        const studentPlacements = placements.filter(
            placement => placement.student_id === 1
        );

        if (studentPlacements.length === 0) {
            alert("No placement details found.");
            return;
        }

        let placementDetails = "";

        studentPlacements.forEach(function(placement) {
            placementDetails +=
                 "<div class='placement-card'>" +
                "<h3>Placement #" + placement.placement_id + "</h3>" +
                "<p><strong>Company ID:</strong> " + placement.company_id + "</p>" +
                "<p><strong>Job ID:</strong> " + placement.job_id + "</p>" +
                "<p><strong>Package:</strong> " + placement.package_lpa + " LPA</p>" +
                "<p><strong>Placement Date:</strong> " + placement.placement_date + "</p>" +
                "</div>";
        });

        document.getElementById("dashboardContent").innerHTML =
            "<div class='placement-box'>" +
            "<h2>My Placement</h2>" +
            placementDetails + 
            "</div>";

    } catch (error) {
        alert("Unable to load placement details.");
    }
}

