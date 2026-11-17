
import sqlite3
from datetime import datetime


def get_connection():
    return sqlite3.connect("studymate.db")


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            study_date TEXT NOT NULL,
            hours INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            quiz_date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def add_note(title, content):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (title, content)
    )

    conn.commit()
    conn.close()


def get_notes():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes ORDER BY id DESC")
    notes = cursor.fetchall()

    conn.close()
    return notes


def delete_note(note_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    conn.commit()
    conn.close()


def add_study_plan(subject, study_date, hours):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO study_plans
        (subject, study_date, hours)
        VALUES (?, ?, ?)""",
        (subject, str(study_date), hours)
    )

    conn.commit()
    conn.close()


def get_study_plans():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM study_plans ORDER BY study_date"
    )

    plans = cursor.fetchall()

    conn.close()
    return plans


def add_quiz_result(topic, score, total_questions, percentage):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO quiz_results
        (topic, score, total_questions, percentage, quiz_date)
        VALUES (?, ?, ?, ?, ?)""",
        (
            topic,
            score,
            total_questions,
            percentage,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()


def get_quiz_results():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM quiz_results ORDER BY id DESC"
    )

    results = cursor.fetchall()

    conn.close()
    return results


create_tables()
