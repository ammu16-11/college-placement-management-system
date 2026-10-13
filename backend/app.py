from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import jwt
from datetime import datetime, timedelta, timezone
from flask import send_from_directory

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config["MYSQL_HOST"] = os.getenv("DB_HOST")
app.config["MYSQL_PORT"] = int(os.getenv("DB_PORT", 3306))
app.config["MYSQL_USER"] = os.getenv("DB_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("DB_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("DB_NAME")

mysql = MySQL(app)

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads", "resumes")
ALLOWED_RESUME_EXTENSIONS = {"pdf"}
MAX_RESUME_SIZE = 5 * 1024 * 1024

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_RESUME_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_authenticated_user():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    secret_key = os.getenv("JWT_SECRET_KEY")

    if not token or not secret_key:
        return None

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"]
        )

        user_id = int(payload["user_id"])
        role = payload["role"]
        token_id = payload.get("jti")

        if role == "STUDENT":
            if not token_id:
                return None

            cursor = mysql.connection.cursor()
            try:
                cursor.execute(
                    """
                    SELECT session_id
                    FROM student_sessions
                    WHERE user_id = %s
                      AND token_jti = %s
                      AND expires_at > UTC_TIMESTAMP()
                    LIMIT 1
                    """,
                    (user_id, token_id)
                )

                session = cursor.fetchone()

                if not session:
                    return None

            finally:
                cursor.close()

        return {
            "user_id": user_id,
            "role": role
        }

    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        return None



@app.route("/logout", methods=["POST"])
def logout():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    token = auth_header.split(" ", 1)[1].strip()
    secret_key = os.getenv("JWT_SECRET_KEY")

    if not token or not secret_key:
        return jsonify({
            "status": "error",
            "message": "Invalid token"
        }), 401

    cursor = None

    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"]
        )

        user_id = int(payload["user_id"])
        role = payload["role"]
        token_id = payload.get("jti")

        if role == "STUDENT":
            if not token_id:
                return jsonify({
                    "status": "error",
                    "message": "Invalid student session"
                }), 401

            cursor = mysql.connection.cursor()
            cursor.execute(
                """
                DELETE FROM student_sessions
                WHERE user_id = %s AND token_jti = %s
                """,
                (user_id, token_id)
            )

            deleted_rows = cursor.rowcount

            if deleted_rows == 0:
                mysql.connection.rollback()
                return jsonify({
                    "status": "error",
                    "message": "No matching active session found"
                }), 404

            mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": "Logged out successfully"
        }), 200

    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        if cursor:
            mysql.connection.rollback()

        return jsonify({
            "status": "error",
            "message": "Invalid or expired token"
        }), 401

    except Exception:
        if cursor:
            mysql.connection.rollback()

        app.logger.exception("Logout failed")
        return jsonify({
            "status": "error",
            "message": "Unable to log out"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/officer/active-student-sessions", methods=["GET"])
def active_student_sessions():
    auth_user = get_authenticated_user()

    if not auth_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if auth_user["role"] != "OFFICER":
        return jsonify({
            "status": "error",
            "message": "Officer access required"
        }), 403

    cursor = None

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id)
            FROM student_sessions
            WHERE expires_at > UTC_TIMESTAMP()
        """)
        result = cursor.fetchone()

        return jsonify({
            "status": "success",
            "active_students": int(result[0])
        })

    except Exception:
        app.logger.exception("Active student session count failed")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve active student sessions"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/students", methods=["GET"])
def get_students():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        if authenticated_user["role"] == "OFFICER":
            cursor.execute("""
                SELECT student_id, user_id, register_number,
                       department, cgpa, phone, resume_url
                FROM students
                ORDER BY student_id
            """)

            rows = cursor.fetchall()

            students = [{
                "student_id": row[0],
                "user_id": row[1],
                "register_number": row[2],
                "department": row[3],
                "cgpa": float(row[4]) if row[4] is not None else None,
                "phone": row[5],
                "resume_url": row[6]
            } for row in rows]

            return jsonify(students)

        if authenticated_user["role"] == "STUDENT":
            cursor.execute("""
                SELECT student_id, user_id, register_number,
                       department, cgpa, phone, resume_url
                FROM students
                WHERE user_id = %s
            """, (authenticated_user["user_id"],))

            row = cursor.fetchone()

            if not row:
                return jsonify({
                    "status": "error",
                    "message": "Student profile not found"
                }), 404

            return jsonify({
                "student_id": row[0],
                "user_id": row[1],
                "register_number": row[2],
                "department": row[3],
                "cgpa": float(row[4]) if row[4] is not None else None,
                "phone": row[5],
                "resume_url": row[6]
            })

        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    except Exception:
        app.logger.exception("Unable to retrieve students")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve student profiles"
        }), 500

    finally:
        if cursor:
            cursor.close()

@app.route("/student/resume", methods=["POST"])
def upload_student_resume():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "STUDENT":
        return jsonify({
            "status": "error",
            "message": "Only students can upload resumes"
        }), 403

    if "resume" not in request.files:
        return jsonify({
            "status": "error",
            "message": "Please select a PDF resume"
        }), 400

    file = request.files["resume"]

    if not file.filename:
        return jsonify({
            "status": "error",
            "message": "Please select a file"
        }), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "status": "error",
            "message": "Only PDF resumes are allowed"
        }), 400

    cursor = None
    saved_path = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT student_id FROM students WHERE user_id = %s",
            (authenticated_user["user_id"],)
        )
        student = cursor.fetchone()

        if not student:
            return jsonify({
                "status": "error",
                "message": "Student profile not found"
            }), 404

        student_id = student[0]
        filename = f"student_{student_id}_{uuid.uuid4().hex}.pdf"
        saved_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(saved_path)

        cursor.execute(
            "UPDATE students SET resume_url = %s WHERE student_id = %s",
            (filename, student_id)
        )
        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": "Resume uploaded successfully",
            "resume_url": filename
        }), 200

    except Exception:
        mysql.connection.rollback()

        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)

        app.logger.exception("Unable to upload student resume")
        return jsonify({
            "status": "error",
            "message": "Unable to upload resume"
        }), 500

    finally:
        if cursor:
            cursor.close()

@app.route("/student/resume", methods=["GET"])
def get_student_resume():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "STUDENT":
        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute(
            "SELECT resume_url FROM students WHERE user_id = %s",
            (authenticated_user["user_id"],)
        )
        row = cursor.fetchone()

        if not row or not row[0]:
            return jsonify({
                "status": "error",
                "message": "No resume uploaded yet"
            }), 404

        filename = row[0]

        if (
            not filename.startswith("student_")
            or not filename.endswith(".pdf")
            or "/" in filename
            or "\\" in filename
        ):
            return jsonify({
                "status": "error",
                "message": "Invalid resume record"
            }), 400

        return send_from_directory(
            app.config["UPLOAD_FOLDER"],
            filename,
            as_attachment=True,
            download_name="my_resume.pdf"
        )

    except Exception:
        app.logger.exception("Unable to retrieve student resume")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve resume"
        }), 500

    finally:
        if cursor:
            cursor.close()

@app.route("/companies", methods=["GET"])
def get_companies():
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT company_id, user_id, company_name,
                   industry, website, phone
            FROM companies
        """)

        rows = cursor.fetchall()
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

    except Exception:
        app.logger.exception("Unable to retrieve companies")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve companies"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/jobs", methods=["GET"])
def get_jobs():
    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT job_id, company_id, job_title,
                   description, eligibility_cgpa,
                   salary, location, deadline, created_at
            FROM jobs
        """)

        rows = cursor.fetchall()
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

    except Exception:
        app.logger.exception("Unable to retrieve jobs")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve jobs"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/jobs", methods=["POST"])
def create_job():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "COMPANY":
        return jsonify({
            "status": "error",
            "message": "Company access required"
        }), 403

    cursor = None

    try:
        data = request.get_json(silent=True) or {}

        required_fields = [
            "company_id",
            "title",
            "eligibility_cgpa",
            "salary_lpa",
            "location",
            "deadline"
        ]

        if any(data.get(field) is None for field in required_fields):
            return jsonify({
                "status": "error",
                "message": "All required job fields must be provided"
            }), 400

        try:
            company_id = int(data["company_id"])
            eligibility_cgpa = float(data["eligibility_cgpa"])
            salary = float(data["salary_lpa"])
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "message": "Company ID, eligibility CGPA, and salary must be valid numbers"
            }), 400

        job_title = data["title"].strip() if isinstance(data["title"], str) else ""
        location = data["location"].strip() if isinstance(data["location"], str) else ""
        deadline = data["deadline"]
        description = data.get("description", "")

        if company_id <= 0 or not job_title or not location:
            return jsonify({
                "status": "error",
                "message": "Invalid company ID, job title, or location"
            }), 400

        if not 0 <= eligibility_cgpa <= 10 or salary <= 0:
            return jsonify({
                "status": "error",
                "message": "CGPA must be between 0 and 10 and salary must be positive"
            }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT company_id
            FROM companies
            WHERE user_id = %s
        """, (authenticated_user["user_id"],))

        company = cursor.fetchone()

        if not company:
            return jsonify({
                "status": "error",
                "message": "Company profile not found"
            }), 404

        if company[0] != company_id:
            return jsonify({
                "status": "error",
                "message": "You can only post jobs for your own company"
            }), 403

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

        return jsonify({
            "status": "success",
            "message": "Job posted successfully!",
            "job_id": job_id
        }), 201

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Unable to create job")
        return jsonify({
            "status": "error",
            "message": "Unable to create job"
        }), 500

    finally:
        if cursor:
            cursor.close()


@app.route("/companies", methods=["POST"])
def add_company():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "OFFICER":
        return jsonify({
            "status": "error",
            "message": "Officer access required"
        }), 403

    cursor = None

    try:
        data = request.get_json(silent=True) or {}

        required_fields = [
            "name",
            "email",
            "password",
            "company_name"
        ]

        if any(
            not isinstance(data.get(field), str) or not data[field].strip()
            for field in required_fields
        ):
            return jsonify({
                "status": "error",
                "message": "Name, email, password, and company_name are required"
            }), 400

        name = data["name"].strip()
        email = data["email"].strip().lower()
        password = data["password"]
        company_name = data["company_name"].strip()

        if len(password) < 8:
            return jsonify({
                "status": "error",
                "message": "Password must contain at least 8 characters"
            }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE email = %s
        """, (email,))

        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Email is already registered"
            }), 409

        cursor.execute("""
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, 'COMPANY')
        """, (
            name,
            email,
            generate_password_hash(password)
        ))

        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO companies
            (user_id, company_name, industry, website, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            company_name,
            data.get("industry"),
            data.get("website"),
            data.get("phone")
        ))

        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": "Company added successfully",
            "user_id": user_id
        }), 201

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Unable to add company")
        return jsonify({
            "status": "error",
            "message": "Unable to add company"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/students", methods=["POST"])
def add_student():
    return jsonify({
        "status": "error",
        "message": "This endpoint is deprecated. Use /register/student instead."
    }), 410




@app.route("/applications", methods=["GET"])
def get_applications():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    role = authenticated_user["role"]

    if role not in ["STUDENT", "OFFICER"]:
        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        if role == "STUDENT":
            cursor.execute("""
                SELECT a.application_id, a.student_id, a.job_id,
                       a.status, a.applied_at
                FROM applications a
                JOIN students s ON a.student_id = s.student_id
                WHERE s.user_id = %s
            """, (authenticated_user["user_id"],))
        else:
            cursor.execute("""
                SELECT application_id, student_id, job_id,
                       status, applied_at
                FROM applications
            """)

        rows = cursor.fetchall()
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

    except Exception:
        app.logger.exception("Unable to retrieve applications")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve applications"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/applications", methods=["POST"])
def create_application():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "STUDENT":
        return jsonify({
            "status": "error",
            "message": "Student access required"
        }), 403

    cursor = None

    try:
        data = request.get_json(silent=True) or {}
        job_id = data.get("job_id")

        if not job_id:
            return jsonify({
                "status": "error",
                "message": "job_id is required"
            }), 400

        try:
            job_id = int(job_id)
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "message": "job_id must be an integer"
            }), 400

        if job_id <= 0:
            return jsonify({
                "status": "error",
                "message": "Invalid job_id"
            }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT student_id
            FROM students
            WHERE user_id = %s
        """, (authenticated_user["user_id"],))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "status": "error",
                "message": "Student profile not found"
            }), 404

        student_id = student[0]

        cursor.execute("""
            SELECT job_id
            FROM jobs
            WHERE job_id = %s
        """, (job_id,))

        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Job not found"
            }), 404

        cursor.execute("""
            SELECT application_id
            FROM applications
            WHERE student_id = %s AND job_id = %s
        """, (student_id, job_id))

        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "You have already applied for this job."
            }), 400

        cursor.execute("""
            INSERT INTO applications
            (student_id, job_id, status)
            VALUES (%s, %s, %s)
        """, (student_id, job_id, "APPLIED"))

        mysql.connection.commit()
        application_id = cursor.lastrowid

        return jsonify({
            "status": "success",
            "message": "Application submitted successfully!",
            "application_id": application_id
        }), 201

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Unable to create application")
        return jsonify({
            "status": "error",
            "message": "Unable to submit application"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/applications/<int:application_id>", methods=["PUT"])
def update_application_status(application_id):
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "OFFICER":
        return jsonify({
            "status": "error",
            "message": "Officer access required"
        }), 403

    cursor = None

    try:
        data = request.get_json(silent=True) or {}
        status = data.get("status")

        allowed_statuses = {"APPLIED", "SHORTLISTED", "REJECTED"}

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

        if not cursor.fetchone():
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

        return jsonify({
            "status": "success",
            "message": "Application status updated successfully!",
            "application_id": application_id,
            "new_status": status
        })

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Unable to update application status")
        return jsonify({
            "status": "error",
            "message": "Unable to update application status"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/interviews", methods=["POST"])
def add_interview():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "OFFICER":
        return jsonify({
            "status": "error",
            "message": "Officer access required"
        }), 403

    cursor = None

    try:
        data = request.get_json(silent=True) or {}

        required_fields = [
            "application_id",
            "interview_date",
            "interview_time"
        ]

        if any(data.get(field) is None for field in required_fields):
            return jsonify({
                "status": "error",
                "message": "application_id, interview_date, and interview_time are required"
            }), 400

        try:
            application_id = int(data["application_id"])
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "message": "application_id must be an integer"
            }), 400

        if application_id <= 0:
            return jsonify({
                "status": "error",
                "message": "Invalid application_id"
            }), 400

        interview_date = data["interview_date"]
        interview_time = data["interview_time"]
        mode = data.get("mode")

        if mode is not None and mode not in {"Online", "Offline"}:
            return jsonify({
                "status": "error",
                "message": "mode must be Online or Offline"
            }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT application_id
            FROM applications
            WHERE application_id = %s
        """, (application_id,))

        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Application not found"
            }), 404

        cursor.execute("""
            INSERT INTO interviews
            (application_id, interview_date, interview_time, mode, result)
            VALUES (%s, %s, %s, %s, 'PENDING')
        """, (
            application_id,
            interview_date,
            interview_time,
            mode
        ))

        interview_id = cursor.lastrowid
        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": "Interview scheduled successfully",
            "interview_id": interview_id
        }), 201

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Unable to schedule interview")
        return jsonify({
            "status": "error",
            "message": "Unable to schedule interview"
        }), 500

    finally:
        if cursor:
            cursor.close()




@app.route("/interviews", methods=["GET"])
def get_interviews():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    role = authenticated_user["role"]

    if role not in ["STUDENT", "OFFICER"]:
        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        if role == "STUDENT":
            cursor.execute("""
                SELECT i.interview_id, i.application_id,
                       i.interview_date, i.interview_time,
                       i.mode, i.result
                FROM interviews i
                JOIN applications a
                    ON i.application_id = a.application_id
                JOIN students s
                    ON a.student_id = s.student_id
                WHERE s.user_id = %s
            """, (authenticated_user["user_id"],))
        else:
            cursor.execute("""
                SELECT interview_id, application_id,
                       interview_date, interview_time,
                       mode, result
                FROM interviews
            """)

        rows = cursor.fetchall()
        interviews = []

        for row in rows:
            interviews.append({
                "interview_id": row[0],
                "application_id": row[1],
                "interview_date": str(row[2]) if row[2] is not None else None,
                "interview_time": str(row[3]) if row[3] is not None else None,
                "mode": row[4],
                "result": row[5]
            })

        return jsonify(interviews)

    except Exception:
        app.logger.exception("Unable to retrieve interviews")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve interviews"
        }), 500

    finally:
        if cursor:
            cursor.close()




@app.route("/interviews/<int:interview_id>", methods=["PUT"])
def update_interview_result(interview_id):
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "OFFICER":
        return jsonify({
            "status": "error",
            "message": "Officer access required"
        }), 403

    cursor = None

    try:
        data = request.get_json(silent=True) or {}
        result = data.get("result")

        allowed_results = {"PENDING", "PASSED", "FAILED"}

        if result not in allowed_results:
            return jsonify({
                "status": "error",
                "message": "Result must be PENDING, PASSED, or FAILED"
            }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT interview_id
            FROM interviews
            WHERE interview_id = %s
        """, (interview_id,))

        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Interview not found"
            }), 404

        cursor.execute("""
            UPDATE interviews
            SET result = %s
            WHERE interview_id = %s
        """, (result, interview_id))

        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": "Interview result updated successfully"
        })

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Unable to update interview result")
        return jsonify({
            "status": "error",
            "message": "Unable to update interview result"
        }), 500

    finally:
        if cursor:
            cursor.close()




@app.route("/placements", methods=["GET"])
def get_placements():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    role = authenticated_user["role"]

    if role not in ["STUDENT", "OFFICER"]:
        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        if role == "STUDENT":
            cursor.execute("""
                SELECT p.placement_id, p.student_id, p.company_id,
                       p.job_id, p.package_lpa, p.placement_date
                FROM placements p
                JOIN students s ON p.student_id = s.student_id
                WHERE s.user_id = %s
            """, (authenticated_user["user_id"],))
        else:
            cursor.execute("""
                SELECT placement_id, student_id, company_id,
                       job_id, package_lpa, placement_date
                FROM placements
            """)

        rows = cursor.fetchall()
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

    except Exception:
        app.logger.exception("Unable to retrieve placements")
        return jsonify({
            "status": "error",
            "message": "Unable to retrieve placements"
        }), 500

    finally:
        if cursor:
            cursor.close()


@app.route("/placements", methods=["POST"])
def add_placement():
    authenticated_user = get_authenticated_user()

    if not authenticated_user:
        return jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401

    if authenticated_user["role"] != "OFFICER":
        return jsonify({
            "status": "error",
            "message": "Officer access required"
        }), 403

    cursor = None

    try:
        data = request.get_json(silent=True) or {}

        required_fields = ["student_id", "company_id", "job_id"]

        if any(data.get(field) is None for field in required_fields):
            return jsonify({
                "status": "error",
                "message": "student_id, company_id, and job_id are required"
            }), 400

        try:
            student_id = int(data["student_id"])
            company_id = int(data["company_id"])
            job_id = int(data["job_id"])
        except (TypeError, ValueError):
            return jsonify({
                "status": "error",
                "message": "Student, company, and job IDs must be integers"
            }), 400

        if min(student_id, company_id, job_id) <= 0:
            return jsonify({
                "status": "error",
                "message": "IDs must be positive integers"
            }), 400

        package_lpa = data.get("package_lpa")

        if package_lpa is not None:
            try:
                package_lpa = float(package_lpa)
                if package_lpa <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                return jsonify({
                    "status": "error",
                    "message": "package_lpa must be a positive number"
                }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT student_id FROM students
            WHERE student_id = %s
        """, (student_id,))

        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Student not found"
            }), 404

        cursor.execute("""
            SELECT company_id FROM companies
            WHERE company_id = %s
        """, (company_id,))

        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Company not found"
            }), 404

        cursor.execute("""
            SELECT job_id, company_id FROM jobs
            WHERE job_id = %s
        """, (job_id,))

        job = cursor.fetchone()

        if not job:
            return jsonify({
                "status": "error",
                "message": "Job not found"
            }), 404

        if job[1] != company_id:
            return jsonify({
                "status": "error",
                "message": "The job does not belong to the selected company"
            }), 400

        cursor.execute("""
            SELECT application_id
            FROM applications
            WHERE student_id = %s
            AND job_id = %s
            LIMIT 1
        """, (student_id, job_id))

        if not cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "The student must apply for this job before a placement can be recorded"
            }), 400

        cursor.execute("""
            INSERT INTO placements
            (student_id, company_id, job_id, package_lpa, placement_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            student_id,
            company_id,
            job_id,
            package_lpa,
            data.get("placement_date")
        ))

        placement_id = cursor.lastrowid
        mysql.connection.commit()

        return jsonify({
            "status": "success",
            "message": "Placement added successfully",
            "placement_id": placement_id
        }), 201

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Unable to add placement")
        return jsonify({
            "status": "error",
            "message": "Unable to add placement"
        }), 500

    finally:
        if cursor:
            cursor.close()

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
            password_valid = check_password_hash(stored_password, password)
        else:
            password_valid = stored_password == password
            if password_valid:
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "UPDATE users SET password = %s WHERE user_id = %s",
                    (hashed_password, user[0])
                )
                mysql.connection.commit()

        if not password_valid:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        secret_key = os.getenv("JWT_SECRET_KEY")
        if not secret_key:
            return jsonify({
                "status": "error",
                "message": "Authentication configuration is missing"
            }), 500

        
        token_id = str(uuid.uuid4())
        token_expiry = datetime.now(timezone.utc) + timedelta(hours=2)

        token = jwt.encode(
            {
                "sub": str(user[0]),
                "user_id": user[0],
                "role": user[3],
                "jti": token_id,
                "exp": token_expiry
            },
            secret_key,
            algorithm="HS256"
        )

        
        if user[3] == "STUDENT":
            cursor.execute(
                """
                INSERT INTO student_sessions (user_id, token_jti, expires_at)
                VALUES (%s, %s, %s)
                """,
                (
                    user[0],
                    token_id,
                    token_expiry.astimezone(timezone.utc).replace(tzinfo=None)
                )
            )
            mysql.connection.commit()



        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user_id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "access_token": token
        })

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Login failed")
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
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "A valid JSON object is required"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    company_name = data.get("company_name")
    industry = data.get("industry", "")
    website = data.get("website", "")
    phone = data.get("phone", "")

    required_values = [name, email, password, company_name]

    if not all(isinstance(value, str) for value in required_values):
        return jsonify({
            "status": "error",
            "message": "Name, email, password, and company name must be text"
        }), 400

    optional_values = [industry, website, phone]

    if not all(isinstance(value, str) for value in optional_values):
        return jsonify({
            "status": "error",
            "message": "Industry, website, and phone must be text"
        }), 400

    name = name.strip()
    email = email.strip().lower()
    company_name = company_name.strip()
    industry = industry.strip()
    website = website.strip()
    phone = phone.strip()

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

        app.logger.exception("Unable to register company")

        return jsonify({
            "status": "error",
            "message": "Unable to create company account"
        }), 500

    finally:
        if cursor:
            cursor.close()



@app.route("/db-test")
def db_test():
    cursor = None

    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE()")
        database = cursor.fetchone()

        return jsonify({
            "status": "success",
            "database": database[0]
        })

    except Exception:
        app.logger.exception("Database health check failed")

        return jsonify({
            "status": "error",
            "message": "Database health check failed"
        }), 500

    finally:
        if cursor:
            cursor.close()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)