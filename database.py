import sqlite3

# =========================
# Connect Database
# =========================

conn = sqlite3.connect("defence.db")
cursor = conn.cursor()


# =========================
# USERS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
)
""")


# =========================
# NOTIFICATIONS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    organization TEXT NOT NULL,
    start_date TEXT NOT NULL,
    last_date TEXT NOT NULL,
    apply_link TEXT NOT NULL
)
""")

# ================= CONTACT TABLE =================

cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT NOT NULL,

    subject TEXT NOT NULL,

    message TEXT NOT NULL

)
""")


# =========================
# CONTACTS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL
)
""")


# =========================
# SAVE CHANGES
# =========================

conn.commit()


# =========================
# CLOSE DATABASE
# =========================

conn.close()


print("Database Created Successfully!")