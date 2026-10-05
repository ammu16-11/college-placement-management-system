CREATE DATABASE IF NOT EXISTS college_placement;

USE college_placement;

-- Main login table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('STUDENT', 'COMPANY', 'OFFICER') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student information
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    register_number VARCHAR(50) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    cgpa DECIMAL(3,2),
    phone VARCHAR(20),
    resume_url VARCHAR(500),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- Company information
CREATE TABLE IF NOT EXISTS companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    website VARCHAR(255),
    phone VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- Job postings
CREATE TABLE IF NOT EXISTS jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    description TEXT,
    eligibility_cgpa DECIMAL(3,2),
    salary DECIMAL(12,2),
    location VARCHAR(150),
    deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE CASCADE
);

-- Student applications
CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    status ENUM('APPLIED', 'SHORTLISTED', 'REJECTED', 'SELECTED')
        DEFAULT 'APPLIED',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
        ON DELETE CASCADE,
    UNIQUE(student_id, job_id)
);

-- Interviews
CREATE TABLE IF NOT EXISTS interviews (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    interview_date DATE NOT NULL,
    interview_time TIME NOT NULL,
    mode VARCHAR(50),
    result ENUM('PENDING', 'PASSED', 'FAILED') DEFAULT 'PENDING',
    FOREIGN KEY (application_id) REFERENCES applications(application_id)
        ON DELETE CASCADE
);

-- Final placement records
CREATE TABLE IF NOT EXISTS placements (
    placement_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    company_id INT NOT NULL,
    job_id INT NOT NULL,
    package_lpa DECIMAL(6,2),
    placement_date DATE,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
);