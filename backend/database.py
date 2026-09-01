import sqlite3

DB_PATH = "database/week24.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS studyplan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        percentage INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teacher_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        student_id INTEGER,
        FOREIGN KEY(teacher_id) REFERENCES users(id),
        FOREIGN KEY(student_id) REFERENCES users(id)
    )
    """)


    conn.commit()
    conn.close()

def get_db():
    return sqlite3.connect(DB_PATH)
