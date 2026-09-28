from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash

from models.database import (
    init_db,
    get_user_by_email,
    create_user,
    save_assessment,
    get_latest_assessment,
    get_user_progress,
    save_quiz_result,
    get_courses
)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app = Flask(__name__)

app.secret_key = "capacity-connect-secret-key-2026"


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_db()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Please enter email and password.", "error")
            return redirect(url_for("login"))

        user = get_user_by_email(email)

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            flash("Login successful!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            flash("Please fill all fields.", "error")
            return redirect(url_for("register"))

        existing_user = get_user_by_email(email)

        if existing_user:
            flash("Email already registered.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        create_user(
            name=name,
            email=email,
            password=hashed_password,
            role="learner"
        )

        flash("Registration successful. Please login.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("login"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    role = session.get("role")

    if role == "admin":
        return render_template(
            "admin_dashboard.html",
            name=session.get("name")
        )

    if role == "trainer":
        return render_template(
            "trainer_dashboard.html",
            name=session.get("name")
        )

    assessment = get_latest_assessment(session["user_id"])

    progress = get_user_progress(session["user_id"])

    return render_template(
        "learner_dashboard.html",
        name=session.get("name"),
        assessment=assessment,
        progress=progress
    )


# ============================================================
# SKILL ASSESSMENT
# ============================================================

@app.route("/assessment", methods=["GET", "POST"])
def assessment():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "learner":
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        python_score = int(request.form.get("python", 0))
        programming_score = int(request.form.get("programming", 0))
        database_score = int(request.form.get("database", 0))
        web_score = int(request.form.get("web", 0))
        data_score = int(request.form.get("data", 0))

        total_score = (
            python_score +
            programming_score +
            database_score +
            web_score +
            data_score
        )

        average_score = total_score / 5

        if average_score >= 80:
            level = "Advanced"
        elif average_score >= 50:
            level = "Intermediate"
        else:
            level = "Beginner"

        save_assessment(
            user_id=session["user_id"],
            python_score=python_score,
            programming_score=programming_score,
            database_score=database_score,
            web_score=web_score,
            data_score=data_score,
            average_score=average_score,
            level=level
        )

        flash(
            "Assessment completed successfully!",
            "success"
        )

        return redirect(url_for("learning_path"))

    return render_template(
        "skill_assessment.html",
        name=session.get("name")
    )


# ============================================================
# AI LEARNING PATH
# ============================================================

@app.route("/learning-path")
def learning_path():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "learner":
        return redirect(url_for("dashboard"))

    assessment_data = get_latest_assessment(
        session["user_id"]
    )

    if not assessment_data:

        flash(
            "Please complete your skill assessment first.",
            "error"
        )

        return redirect(url_for("assessment"))

    scores = {
        "Python": assessment_data["python_score"],
        "Programming": assessment_data["programming_score"],
        "Database": assessment_data["database_score"],
        "Web Development": assessment_data["web_score"],
        "Data Analysis": assessment_data["data_score"]
    }

    weakest_skill = min(
        scores,
        key=scores.get
    )

    learning_paths = {

        "Python": [
            "Python Fundamentals",
            "Object-Oriented Programming",
            "Python for Data Science",
            "Python Project Development"
        ],

        "Programming": [
            "Programming Fundamentals",
            "Data Structures",
            "Algorithms",
            "Problem Solving Projects"
        ],

        "Database": [
            "SQL Fundamentals",
            "Database Design",
            "Advanced SQL",
            "Database Project"
        ],

        "Web Development": [
            "HTML & CSS",
            "JavaScript Fundamentals",
            "Flask Web Development",
            "Full Stack Project"
        ],

        "Data Analysis": [
            "Excel Fundamentals",
            "Python for Data Analysis",
            "Pandas & Visualization",
            "Data Analytics Project"
        ]
    }

    recommended_path = learning_paths[weakest_skill]

    return render_template(
        "learning_path.html",
        name=session.get("name"),
        assessment=assessment_data,
        weakest_skill=weakest_skill,
        recommended_path=recommended_path
    )


# ============================================================
# COURSES
# ============================================================

@app.route("/courses")
def courses():

    if "user_id" not in session:
        return redirect(url_for("login"))

    course_list = get_courses()

    return render_template(
        "course.html",
        courses=course_list,
        name=session.get("name")
    )


# ============================================================
# QUIZ
# ============================================================

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        answers = {
            "q1": request.form.get("q1"),
            "q2": request.form.get("q2"),
            "q3": request.form.get("q3"),
            "q4": request.form.get("q4"),
            "q5": request.form.get("q5")
        }

        correct_answers = {
            "q1": "python",
            "q2": "database",
            "q3": "html",
            "q4": "algorithm",
            "q5": "pandas"
        }

        score = 0

        for question in correct_answers:

            if answers.get(question) == correct_answers[question]:
                score += 1

        percentage = (score / 5) * 100

        save_quiz_result(
            user_id=session["user_id"],
            score=score,
            percentage=percentage
        )

        flash(
            f"Quiz completed! Score: {score}/5",
            "success"
        )

        return redirect(url_for("progress"))

    return render_template(
        "quiz.html",
        name=session.get("name")
    )


# ============================================================
# PROGRESS
# ============================================================

@app.route("/progress")
def progress():

    if "user_id" not in session:
        return redirect(url_for("login"))

    progress_data = get_user_progress(
        session["user_id"]
    )

    assessment_data = get_latest_assessment(
        session["user_id"]
    )

    return render_template(
        "progress.html",
        name=session.get("name"),
        progress=progress_data,
        assessment=assessment_data
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )