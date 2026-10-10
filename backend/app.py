from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["MYSQL_HOST"] = os.getenv("DB_HOST")
app.config["MYSQL_PORT"] = int(os.getenv("DB_PORT", 3306))
app.config["MYSQL_USER"] = os.getenv("DB_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("DB_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("DB_NAME")

mysql = MySQL(app)

@app.route("/students", methods=["GET"])
def get_students():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT student_id, user_id, register_number,
                   department, cgpa, phone, resume_url
            FROM students
        """)
        rows = cursor.fetchall()
        cursor.close()

        students = []

        for row in rows:
            students.append({
                "student_id": row[0],
                "user_id": row[1],
                "register_number": row[2],
                "department": row[3],
                "cgpa": float(row[4]) if row[4] is not None else None,
                "phone": row[5],
                "resume_url": row[6]
            })

        return jsonify(students)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/companies", methods=["GET"])
def get_companies():
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT company_id, user_id, company_name,
                   industry, website, phone
            FROM companies
        """)

        rows = cursor.fetchall()
        cursor.close()

        companies = []

        for row in rows:
            companies.append({
                "company_id": row[0],
                "user_id": row[1],
                "company_name": row[2],
                "industry": row[3],
                "website": row[4],
                "phone": row[5]
            })

        return jsonify(companies)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/jobs", methods=["GET"])
def get_jobs():
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT job_id, company_id, job_title,
                   description, eligibility_cgpa,
                   salary, location, deadline, created_at
            FROM jobs
        """)

        rows = cursor.fetchall()
        cursor.close()

        jobs = []

        for row in rows:
            jobs.append({
                "job_id": row[0],
                "company_id": row[1],
                "job_title": row[2],
                "description": row[3],
                "eligibility_cgpa": float(row[4]) if row[4] is not None else None,
                "salary": float(row[5]) if row[5] is not None else None,
                "location": row[6],
                "deadline": str(row[7]) if row[7] is not None else None,
                "created_at": str(row[8]) if row[8] is not None else None
            })

        return jsonify(jobs)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/jobs", methods=["POST"])
def create_job():
    try:
        data = request.get_json()

        print("JOB DATA RECEIVED:", data)

        company_id = data["company_id"]
        job_title = data["title"]
        description = data.get("description", "")
        eligibility_cgpa = data["eligibility_cgpa"]
        salary = data["salary_lpa"]
        location = data["location"]
        deadline = data["deadline"]

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO jobs
            (company_id, job_title, description, eligibility_cgpa,
             salary, location, deadline)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            company_id,
            job_title,
            description,
            eligibility_cgpa,
            salary,
            location,
            deadline
        ))

        mysql.connection.commit()

        job_id = cursor.lastrowid

        cursor.close()

        print("JOB CREATED:", job_id)

        return jsonify({
            "status": "success",
            "message": "Job posted successfully!",
            "job_id": job_id
        }), 201

    except Exception as e:
        print("JOB INSERT ERROR:", str(e))
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/companies", methods=["POST"])
def add_company():
    try:
        data = request.get_json()

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'COMPANY')
        """, (
            data["name"],
            data["email"],
            data["password"]
        ))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO companies
            (user_id, company_name, industry, website, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            data["company_name"],
            data.get("industry"),
            data.get("website"),
            data.get("phone")
        ))

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Company added successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/students", methods=["POST"])
def add_student():
    try:
        data = request.get_json()

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'STUDENT')
        """, (
            data["name"],
            data["email"],
            data["password"]
        ))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO students
            (user_id, register_number, department, cgpa, phone, resume_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            data["register_number"],
            data["department"],
            data.get("cgpa"),
            data.get("phone"),
            data.get("resume_url")
        ))

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Student added successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/applications", methods=["GET"])
def get_applications():
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT application_id, student_id, job_id,
                   status, applied_at
            FROM applications
        """)

        rows = cursor.fetchall()
        cursor.close()

        applications = []

        for row in rows:
            applications.append({
                "application_id": row[0],
                "student_id": row[1],
                "job_id": row[2],
                "status": row[3],
                "applied_at": str(row[4]) if row[4] is not None else None
            })

        return jsonify(applications)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/applications", methods=["POST"])
def create_application():
    try:
        data = request.get_json()

        student_id = data["student_id"]
        job_id = data["job_id"]

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT application_id
            FROM applications
            WHERE student_id = %s AND job_id = %s
        """, (student_id, job_id))

        existing = cursor.fetchone()

        if existing:
            cursor.close()

            return jsonify({
                "status": "error",
                "message": "You have already applied for this job."
            }), 400

        cursor.execute("""
            INSERT INTO applications
            (student_id, job_id, status)
            VALUES (%s, %s, %s)
        """, (
            student_id,
            job_id,
            "APPLIED"
        ))

        mysql.connection.commit()

        application_id = cursor.lastrowid

        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Application submitted successfully!",
            "application_id": application_id
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/applications/<int:application_id>", methods=["PUT"])
def update_application_status(application_id):
    try:
        data = request.get_json()

        status = data["status"]

        allowed_statuses = ["APPLIED", "SHORTLISTED", "REJECTED"]

        if status not in allowed_statuses:
            return jsonify({
                "status": "error",
                "message": "Invalid application status."
            }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT application_id
            FROM applications
            WHERE application_id = %s
        """, (application_id,))

        application = cursor.fetchone()

        if not application:
            cursor.close()

            return jsonify({
                "status": "error",
                "message": "Application not found."
            }), 404

        cursor.execute("""
            UPDATE applications
            SET status = %s
            WHERE application_id = %s
        """, (status, application_id))

        mysql.connection.commit()

        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Application status updated successfully!",
            "application_id": application_id,
            "new_status": status
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/interviews", methods=["POST"])
def add_interview():
    try:
        data = request.get_json()

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO interviews
            (application_id, interview_date, interview_time, mode, result)
            VALUES (%s, %s, %s, %s, 'PENDING')
        """, (
            data["application_id"],
            data["interview_date"],
            data["interview_time"],
            data.get("mode")
        ))

        interview_id = cursor.lastrowid

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Interview scheduled successfully",
            "interview_id": interview_id
        }), 201

    except Exception as e:
        mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/interviews", methods=["GET"])
def get_interviews():
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT interview_id, application_id,
                   interview_date, interview_time,
                   mode, result
            FROM interviews
        """)

        rows = cursor.fetchall()
        cursor.close()

        interviews = []

        for row in rows:
            interviews.append({
                "interview_id": row[0],
                "application_id": row[1],
                "interview_date": str(row[2]),
                "interview_time": str(row[3]),
                "mode": row[4],
                "result": row[5]
            })

        return jsonify(interviews)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/interviews/<int:interview_id>", methods=["PUT"])
def update_interview_result(interview_id):
    try:
        data = request.get_json()
        result = data["result"]

        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE interviews
            SET result = %s
            WHERE interview_id = %s
        """, (result, interview_id))

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Interview result updated successfully"
        })

    except Exception as e:
        mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/placements", methods=["GET"])
def get_placements():
    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT placement_id, student_id, company_id,
                   job_id, package_lpa, placement_date
            FROM placements
        """)

        rows = cursor.fetchall()
        cursor.close()

        placements = []

        for row in rows:
            placements.append({
                "placement_id": row[0],
                "student_id": row[1],
                "company_id": row[2],
                "job_id": row[3],
                "package_lpa": float(row[4]) if row[4] is not None else None,
                "placement_date": str(row[5]) if row[5] is not None else None
            })

        return jsonify(placements)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/placements", methods=["POST"])
def add_placement():
    try:
        data = request.get_json()

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO placements
            (student_id, company_id, job_id, package_lpa, placement_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data["student_id"],
            data["company_id"],
            data["job_id"],
            data.get("package_lpa"),
            data.get("placement_date")
        ))

        placement_id = cursor.lastrowid

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            "status": "success",
            "message": "Placement added successfully",
            "placement_id": placement_id
        }), 201

    except Exception as e:
        mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/")
def home():
    return "College Placement Management System is running!"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required"
        }), 400

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT user_id, name, email, role, password
            FROM users
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        stored_password = user[4]

        if stored_password.startswith(("scrypt:", "pbkdf2:")):
            password_valid = check_password_hash(
                stored_password, password
            )
        else:
            password_valid = stored_password == password

            if password_valid:
                hashed_password = generate_password_hash(password)

                cursor.execute("""
                    UPDATE users
                    SET password = %s
                    WHERE user_id = %s
                """, (hashed_password, user[0]))

                mysql.connection.commit()

        if not password_valid:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user_id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3]
        })

    except Exception:
        mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Unable to process login"
        }), 500

    finally:
        if cursor:
            cursor.close()


@app.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    register_number = data.get("register_number", "").strip()
    department = data.get("department", "").strip()
    phone = data.get("phone", "").strip()
    cgpa = data.get("cgpa")

    if not all([name, email, password, register_number, department]):
        return jsonify({
            "status": "error",
            "message": "Please fill in all required fields"
        }), 400

    if len(password) < 8:
        return jsonify({
            "status": "error",
            "message": "Password must contain at least 8 characters"
        }), 400

    try:
        cgpa = float(cgpa)

        if not 0 <= cgpa <= 10:
            raise ValueError

    except (TypeError, ValueError):
        return jsonify({
            "status": "error",
            "message": "CGPA must be between 0 and 10"
        }), 400

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Email already registered"
            }), 409

        cursor.execute(
            "SELECT student_id FROM students WHERE register_number = %s",
            (register_number,)
        )

        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Register number already exists"
            }), 409

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'STUDENT')
        """, (name, email, hashed_password))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO students
            (user_id, register_number, department, cgpa, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            register_number,
            department,
            cgpa,
            phone or None
        ))

        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": "Student account created successfully",
            "user_id": user_id
        }), 201

    except Exception:
        if cursor:
            mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Unable to create student account"
        }), 500

    finally:
        if cursor:
            cursor.close()

@app.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    company_name = data.get("company_name", "").strip()
    industry = data.get("industry", "").strip()
    website = data.get("website", "").strip()
    phone = data.get("phone", "").strip()

    if not all([name, email, password, company_name]):
        return jsonify({
            "status": "error",
            "message": "Name, email, password, and company name are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "status": "error",
            "message": "Password must contain at least 8 characters"
        }), 400

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Email already registered"
            }), 409

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'COMPANY')
        """, (name, email, hashed_password))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO companies
            (user_id, company_name, industry, website, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            company_name,
            industry or None,
            website or None,
            phone or None
        ))

        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": "Company account created successfully",
            "user_id": user_id
        }), 201

    except Exception:
        if cursor:
            mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Unable to create company account"
        }), 500

    finally:
        if cursor:
            cursor.close()

@app.route("/db-test")
def db_test():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE()")
        database = cursor.fetchone()
        cursor.close()

        return jsonify({
            "status": "success",
            "database": database[0]
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)