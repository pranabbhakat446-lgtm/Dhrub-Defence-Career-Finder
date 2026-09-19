from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "dhrub_defence_secret_key"


# ========================= USER LOGIN PAGE =========================

@app.route("/")
def login():
    return render_template("login.html")


# ========================= USER LOGIN =========================

@app.route("/login", methods=["POST"])
def login_user():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("defence.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        session["user"] = username
        return redirect("/home")

    return "Invalid Username or Password"


# ========================= HOME =========================

@app.route("/home")
def home():

    if "user" not in session:
        return redirect("/")

    return render_template("home.html")


# ========================= SIGNUP =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("defence.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,email,password) VALUES(?,?,?)",
            (username, email, password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")


# ========================= ELIGIBILITY =========================

@app.route("/eligibility")
def eligibility():

    if "user" not in session:
        return redirect("/")

    return render_template("eligibility.html")


# ========================= ELIGIBILITY CHECK =========================

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

# ========================= NOTIFICATIONS =========================

@app.route("/notifications")
def notifications():

    organization = request.args.get("organization")

    conn = sqlite3.connect("defence.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if organization:

        jobs = cursor.execute(
            """
            SELECT *
            FROM notifications
            WHERE organization=?
            ORDER BY id DESC
            """,
            (organization,)
        ).fetchall()

    else:

        jobs = cursor.execute(
            """
            SELECT *
            FROM notifications
            ORDER BY id DESC
            """
        ).fetchall()

    conn.close()

    return render_template(
        "notifications.html",
        jobs=jobs,
        organization=organization
    )
    # ---------------- Army Jobs ----------------
@app.route("/army-jobs")
def army_jobs():

    conn = sqlite3.connect("defence.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM notifications
        WHERE organization LIKE '%Army%'
        ORDER BY id DESC
    """)

    jobs = cur.fetchall()
    conn.close()

    return render_template("notifications.html", jobs=jobs)


# ---------------- Navy Jobs ----------------
@app.route("/navy-jobs")
def navy_jobs():

    conn = sqlite3.connect("defence.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM notifications
        WHERE organization LIKE '%Navy%'
        ORDER BY id DESC
    """)

    jobs = cur.fetchall()
    conn.close()

    return render_template("notifications.html", jobs=jobs)


# ---------------- Air Force Jobs ----------------
@app.route("/airforce-jobs")
def airforce_jobs():

    conn = sqlite3.connect("defence.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM notifications
        WHERE organization LIKE '%Air Force%'
        ORDER BY id DESC
    """)

    jobs = cur.fetchall()
    conn.close()

    return render_template("notifications.html", jobs=jobs)

# ========================= ABOUT US =========================

@app.route("/about")
def about():

    if "user" not in session:
        return redirect("/")

    return render_template("about.html")


# ========================= CONTACT =========================

@app.route("/contact")
def contact():

    if "user" not in session:
        return redirect("/")

    return render_template("contact.html")

 #========================= SEND CONTACT MESSAGE =========================

@app.route("/send-message", methods=["POST"])
def send_message():

    if "user" not in session:
        return redirect("/")

    name = request.form["name"]
    email = request.form["email"]
    subject = request.form["subject"]
    message = request.form["message"]

    conn = sqlite3.connect("defence.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO contacts(name, email, subject, message)
        VALUES (?, ?, ?, ?)
    """, (name, email, subject, message))

    conn.commit()
    conn.close()

    # Success message
    session["contact_success"] = "Message sent successfully! ✅"

    return redirect("/contact")



# ========================= FORGOT PASSWORD =========================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("defence.db")
        cursor = conn.cursor()

        # Check Email Exists
        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        if user:

            cursor.execute(
                "UPDATE users SET password=? WHERE email=?",
                (password, email)
            )

            conn.commit()
            conn.close()

            return redirect("/")

        conn.close()

        return "Email not found!"

    return render_template("forgot_password.html")


# ========================= USER LOGOUT =========================

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")

# ========================= ADMIN LOGIN PAGE =========================

@app.route("/admin")
def admin():
    return render_template("admin_login.html")


# ========================= ADMIN LOGIN =========================

@app.route("/admin-login", methods=["POST"])
def admin_login():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":
        session["admin"] = username
        return redirect("/admin-dashboard")

    return "Invalid Admin Username or Password"



# ========================= ADMIN DASHBOARD =========================

@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("defence.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Search
    search = request.args.get("search", "").strip()

    if search:
        cursor.execute("""
            SELECT *
            FROM notifications
            WHERE LOWER(title) LIKE LOWER(?)
               OR LOWER(organization) LIKE LOWER(?)
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("""
            SELECT *
            FROM notifications
            ORDER BY id DESC
        """)

    jobs = cursor.fetchall()

    print("Search =", search)
    print("Total Results =", len(jobs))

    for job in jobs:
        print(job["title"], "-", job["organization"])

    # Total Vacancies
    cursor.execute("SELECT COUNT(*) FROM notifications")
    total_jobs = cursor.fetchone()[0]

    # Total Users
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

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

    conn.close()

    return render_template(
        "admin_dashboard.html",
        jobs=jobs,
        users=users,
        contacts=contacts,
        total_jobs=total_jobs,
        total_users=total_users
    )
    

  
# ========================= ADD VACANCY =========================

@app.route("/add-vacancy", methods=["POST"])
def add_vacancy():

    if "admin" not in session:
        return redirect("/admin")

    title = request.form["title"]
    organization = request.form["organization"]
    start_date = request.form["start_date"]
    last_date = request.form["last_date"]
    apply_link = request.form["apply_link"]

    conn = sqlite3.connect("defence.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notifications
        (title, organization, start_date, last_date, apply_link)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        organization,
        start_date,
        last_date,
        apply_link
    ))

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")


# ========================= EDIT VACANCY =========================

@app.route("/edit-vacancy/<int:id>")
def edit_vacancy(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("defence.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notifications WHERE id=?", (id,))
    job = cursor.fetchone()

    conn.close()

    return render_template("edit_vacancy.html", job=job)


# ========================= UPDATE VACANCY =========================

@app.route("/update-vacancy/<int:id>", methods=["POST"])
def update_vacancy(id):

    if "admin" not in session:
        return redirect("/admin")

    title = request.form["title"]
    organization = request.form["organization"]
    start_date = request.form["start_date"]
    last_date = request.form["last_date"]
    apply_link = request.form["apply_link"]

    conn = sqlite3.connect("defence.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notifications
        SET
        title=?,
        organization=?,
        start_date=?,
        last_date=?,
        apply_link=?
        WHERE id=?
    """, (
        title,
        organization,
        start_date,
        last_date,
        apply_link,
        id
    ))

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")


# ========================= DELETE VACANCY =========================

@app.route("/delete-vacancy/<int:id>")
def delete_vacancy(id):

    if "admin" not in session:
        return redirect("/admin")

    conn = sqlite3.connect("defence.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notifications WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin-dashboard")


# ========================= ADMIN LOGOUT =========================

@app.route("/admin-logout")
def admin_logout():

    session.pop("admin", None)

    return redirect("/admin")


# ========================= RUN APP =========================

if __name__ == "__main__":
    app.run(debug=True)

    