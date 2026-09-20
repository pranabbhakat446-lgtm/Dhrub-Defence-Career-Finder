import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, session, Response, url_for
import psycopg
from psycopg.rows import dict_row


app = Flask(__name__)
load_dotenv()
app.secret_key = "dhrub_defence_secret_key"


# =========================================================
# DATABASE CONNECTION
# =========================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL environment variable is not set.")

    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


# =========================================================
# CREATE TABLES
# =========================================================

def init_database():

    conn = get_db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # NOTIFICATIONS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications(
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            organization TEXT NOT NULL,
            start_date TEXT NOT NULL,
            last_date TEXT NOT NULL,
            apply_link TEXT NOT NULL
        )
    """)

    # CONTACTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts(
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# =========================================================
# USER LOGIN PAGE
# =========================================================

# =========================================================
# GOOGLE SITEMAP
# =========================================================
@app.route("/sitemap.xml")
def sitemap():
    pages = [
        url_for("login", _external=True),
        url_for("signup", _external=True),
        url_for("home", _external=True),
        url_for("eligibility", _external=True),
        url_for("notifications", _external=True),
        url_for("contact", _external=True)
    ]

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'

    for page in pages:
        sitemap_xml += f"""
        <url>
            <loc>{page}</loc>
        </url>
        """

    sitemap_xml += '</urlset>'

    return Response(sitemap_xml, mimetype="application/xml")
@app.route("/")
def login():
    return render_template("login.html")


# =========================================================
# USER LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login_user():

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE username=%s AND password=%s
        """,
        (username, password)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        session["user"] = username
        return redirect("/home")

    return "Invalid Username or Password"


# =========================================================
# HOME
# =========================================================

@app.route("/home")
def home():

    if "user" not in session:
        return redirect("/")

    return render_template("home.html")


# =========================================================
# SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users(username, email, password)
            VALUES(%s, %s, %s)
            """,
            (username, email, password)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return redirect("/")

    return render_template("signup.html")


# =========================================================
# ELIGIBILITY
# =========================================================

@app.route("/eligibility")
def eligibility():

    if "user" not in session:
        return redirect("/")

    return render_template("eligibility.html")


# =========================================================
# ELIGIBILITY CHECK
# =========================================================

@app.route("/check", methods=["POST"])
def check():

    if "user" not in session:
        return redirect("/")

    gender = request.form["gender"]
    age = int(request.form["age"])
    qualification = request.form["qualification"]

    jobs = []

    # 10th / 12th
    if gender == "Male" and qualification in ["10th", "12th"] and 17 <= age <= 21:
        jobs.append("Indian Army Agniveer")

    # Navy MR
    if gender == "Male" and qualification == "10th" and 17 <= age <= 21:
        jobs.append("Indian Navy MR")

    # Navy SSR
    if gender == "Male" and qualification == "12th" and 17 <= age <= 21:
        jobs.append("Indian Navy SSR")

    # Air Force Agniveer
    if qualification == "12th" and 17 <= age <= 21:
        jobs.append("Indian Air Force Agniveer")

    # Graduate
    if qualification == "Graduate" and 20 <= age <= 25:
        jobs.append("CAPF Assistant Commandant")

    # 8th Pass
    if qualification == "8th":
        jobs.append("Defence Support / Trades Vacancies")

    # ITI
    if qualification == "ITI":
        jobs.append("Defence Technical / Trades Vacancies")

    # Diploma
    if qualification == "Diploma":
        jobs.append("Defence Technical Vacancies")

    # Post Graduate
    if qualification == "Post Graduate":
        jobs.append("Defence Specialist / Officer Vacancies")

    # B.Tech / B.E.
    if qualification == "B.Tech/B.E.":
        jobs.append("Defence Engineering / Technical Vacancies")

    # B.Sc
    if qualification == "B.Sc":
        jobs.append("Defence Science / Technical Vacancies")

    # B.Com
    if qualification == "B.Com":
        jobs.append("Defence Accounts / Administrative Vacancies")

    # B.A.
    if qualification == "B.A.":
        jobs.append("Defence Administrative Vacancies")

    # M.Tech / M.E.
    if qualification == "M.Tech/M.E.":
        jobs.append("Defence Engineering / Specialist Vacancies")

    # Other
    if qualification == "Other":
        jobs.append("Other Defence Vacancies")

    return render_template("result.html", jobs=jobs)


# =========================================================
# NOTIFICATIONS
# =========================================================

@app.route("/notifications")
def notifications():

    organization = request.args.get("organization")

    conn = get_db()
    cursor = conn.cursor()

    if organization:

        cursor.execute(
            """
            SELECT *
            FROM notifications
            WHERE organization=%s
            ORDER BY id DESC
            """,
            (organization,)
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM notifications
            ORDER BY id DESC
            """
        )

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "notifications.html",
        jobs=jobs,
        organization=organization
    )


# =========================================================
# ARMY JOBS
# =========================================================

@app.route("/army-jobs")
def army_jobs():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE organization ILIKE %s
        ORDER BY id DESC
    """, ("%Army%",))

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "notifications.html",
        jobs=jobs
    )


# =========================================================
# NAVY JOBS
# =========================================================

@app.route("/navy-jobs")
def navy_jobs():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE organization ILIKE %s
        ORDER BY id DESC
    """, ("%Navy%",))

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "notifications.html",
        jobs=jobs
    )


# =========================================================
# AIR FORCE JOBS
# =========================================================

@app.route("/airforce-jobs")
def airforce_jobs():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM notifications
        WHERE organization ILIKE %s
        ORDER BY id DESC
    """, ("%Air Force%",))

    jobs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "notifications.html",
        jobs=jobs
    )


# =========================================================
# ABOUT US
# =========================================================

@app.route("/about")
def about():

    if "user" not in session:
        return redirect("/")

    return render_template("about.html")


# =========================================================
# CONTACT
# =========================================================

@app.route("/contact")
def contact():

    if "user" not in session:
        return redirect("/")

    return render_template("contact.html")


# =========================================================
# SEND CONTACT MESSAGE
# =========================================================

@app.route("/send-message", methods=["POST"])
def send_message():

    if "user" not in session:
        return redirect("/")

    name = request.form["name"]
    email = request.form["email"]
    subject = request.form["subject"]
    message = request.form["message"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO contacts(name, email, subject, message)
        VALUES (%s, %s, %s, %s)
        """,
        (name, email, subject, message)
    )

    conn.commit()

    cursor.close()
    conn.close()

    session["contact_success"] = "Message sent successfully! ✅"

    return redirect("/contact")


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if user:

            cursor.execute(
                """
                UPDATE users
                SET password=%s
                WHERE email=%s
                """,
                (password, email)
            )

            conn.commit()

            cursor.close()
            conn.close()

            return redirect("/")

        cursor.close()
        conn.close()

        return "Email not found!"

    return render_template("forgot_password.html")


# =========================================================
# USER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")


# =========================================================
# ADMIN LOGIN PAGE
# =========================================================

@app.route("/admin")
def admin():
    return render_template("admin_login.html")


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/admin-login", methods=["POST"])
def admin_login():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":

        session["admin"] = username

        return redirect("/admin-dashboard")

    return "Invalid Admin Username or Password"


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()

    # Search
    search = request.args.get("search", "").strip()

    if search:

        cursor.execute(
            """
            SELECT *
            FROM notifications
            WHERE title ILIKE %s
               OR organization ILIKE %s
            ORDER BY id DESC
            """,
            (f"%{search}%", f"%{search}%")
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM notifications
            ORDER BY id DESC
            """
        )

    jobs = cursor.fetchall()

    # Total Vacancies
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM notifications
    """)

    total_jobs = cursor.fetchone()["count"]

    # Total Users
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM users
    """)

    total_users = cursor.fetchone()["count"]

    # User List
    cursor.execute("""
        SELECT id, username, email
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    # Contact Messages
    cursor.execute("""
        SELECT *
        FROM contacts
        ORDER BY id DESC
    """)

    contacts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        jobs=jobs,
        users=users,
        contacts=contacts,
        total_jobs=total_jobs,
        total_users=total_users
    )


# =========================================================
# ADD VACANCY
# =========================================================

@app.route("/add-vacancy", methods=["POST"])
def add_vacancy():

    if "admin" not in session:
        return redirect("/admin")

    title = request.form["title"]
    organization = request.form["organization"]
    start_date = request.form["start_date"]
    last_date = request.form["last_date"]
    apply_link = request.form["apply_link"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO notifications
        (title, organization, start_date, last_date, apply_link)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            title,
            organization,
            start_date,
            last_date,
            apply_link
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin-dashboard")


# =========================================================
# EDIT VACANCY
# =========================================================

@app.route("/edit-vacancy/<int:id>")
def edit_vacancy(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM notifications
        WHERE id=%s
        """,
        (id,)
    )

    job = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "edit_vacancy.html",
        job=job
    )


# =========================================================
# UPDATE VACANCY
# =========================================================

@app.route("/update-vacancy/<int:id>", methods=["POST"])
def update_vacancy(id):

    if "admin" not in session:
        return redirect("/admin")

    title = request.form["title"]
    organization = request.form["organization"]
    start_date = request.form["start_date"]
    last_date = request.form["last_date"]
    apply_link = request.form["apply_link"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE notifications
        SET
            title=%s,
            organization=%s,
            start_date=%s,
            last_date=%s,
            apply_link=%s
        WHERE id=%s
        """,
        (
            title,
            organization,
            start_date,
            last_date,
            apply_link,
            id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin-dashboard")


# =========================================================
# DELETE VACANCY
# =========================================================

@app.route("/delete-vacancy/<int:id>")
def delete_vacancy(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM notifications
        WHERE id=%s
        """,
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/admin-dashboard")


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin")


# =========================================================
# INITIALIZE DATABASE
# =========================================================

try:
    init_database()
except Exception as e:
    print("Database initialization error:", e)


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)