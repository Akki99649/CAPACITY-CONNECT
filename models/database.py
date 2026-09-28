import sqlite3
from pathlib import Path


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():

    connection = get_connection()

    cursor = connection.cursor()

    # ---------------- USERS ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'learner',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # ---------------- ASSESSMENTS ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            python_score INTEGER,

            programming_score INTEGER,

            database_score INTEGER,

            web_score INTEGER,

            data_score INTEGER,

            average_score REAL,

            level TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)

    # ---------------- QUIZ RESULTS ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            score INTEGER,

            percentage REAL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)

        )
    """)

    # ---------------- COURSES ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            description TEXT,

            skill TEXT,

            difficulty TEXT,

            duration TEXT

        )
    """)

    connection.commit()

    connection.close()

    insert_default_courses()


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    name,
    email,
    password,
    role="learner"
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users
        (name, email, password, role)

        VALUES (?, ?, ?, ?)
    """, (
        name,
        email,
        password,
        role
    ))

    connection.commit()

    connection.close()


# ============================================================
# GET USER
# ============================================================

def get_user_by_email(email):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    return user


# ============================================================
# SAVE ASSESSMENT
# ============================================================

def save_assessment(
    user_id,
    python_score,
    programming_score,
    database_score,
    web_score,
    data_score,
    average_score,
    level
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO assessments (

            user_id,
            python_score,
            programming_score,
            database_score,
            web_score,
            data_score,
            average_score,
            level

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        python_score,
        programming_score,
        database_score,
        web_score,
        data_score,
        average_score,
        level
    ))

    connection.commit()

    connection.close()


# ============================================================
# GET LATEST ASSESSMENT
# ============================================================

def get_latest_assessment(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM assessments

        WHERE user_id = ?

        ORDER BY created_at DESC

        LIMIT 1
    """, (user_id,))

    assessment = cursor.fetchone()

    connection.close()

    return assessment


# ============================================================
# SAVE QUIZ RESULT
# ============================================================

def save_quiz_result(
    user_id,
    score,
    percentage
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO quiz_results
        (user_id, score, percentage)

        VALUES (?, ?, ?)
    """, (
        user_id,
        score,
        percentage
    ))

    connection.commit()

    connection.close()


# ============================================================
# GET USER PROGRESS
# ============================================================

def get_user_progress(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM quiz_results

        WHERE user_id = ?

        ORDER BY created_at DESC
    """, (user_id,))

    progress = cursor.fetchall()

    connection.close()

    return progress


# ============================================================
# COURSES
# ============================================================

def get_courses():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM courses
        ORDER BY id
    """)

    courses = cursor.fetchall()

    connection.close()

    return courses


# ============================================================
# DEFAULT COURSES
# ============================================================

def insert_default_courses():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM courses
    """)

    count = cursor.fetchone()[0]

    if count == 0:

        courses = [

            (
                "Python Fundamentals",
                "Learn Python programming from basics.",
                "Python",
                "Beginner",
                "4 Weeks"
            ),

            (
                "Data Structures & Algorithms",
                "Learn important programming concepts and algorithms.",
                "Programming",
                "Intermediate",
                "6 Weeks"
            ),

            (
                "SQL & Database Management",
                "Learn SQL queries and database concepts.",
                "Database",
                "Beginner",
                "4 Weeks"
            ),

            (
                "Full Stack Web Development",
                "Build modern web applications using HTML, CSS, JavaScript and Flask.",
                "Web Development",
                "Intermediate",
                "8 Weeks"
            ),

            (
                "Python Data Analysis",
                "Learn Pandas, data processing and visualization.",
                "Data Analysis",
                "Intermediate",
                "6 Weeks"
            )

        ]

        cursor.executemany("""
            INSERT INTO courses
            (
                title,
                description,
                skill,
                difficulty,
                duration
            )

            VALUES (?, ?, ?, ?, ?)
        """, courses)

        connection.commit()

    connection.close()