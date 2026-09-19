import os
import psycopg


# =========================
# CONNECT TO NEON DATABASE
# =========================

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable is not set.")


conn = psycopg.connect(DATABASE_URL)
cursor = conn.cursor()


# =========================
# USERS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
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
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    organization TEXT NOT NULL,
    start_date TEXT NOT NULL,
    last_date TEXT NOT NULL,
    apply_link TEXT NOT NULL
)
""")


# =========================
# CONTACTS TABLE
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS contacts(
    id SERIAL PRIMARY KEY,
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

cursor.close()
conn.close()


print("Neon PostgreSQL Database Created Successfully!")