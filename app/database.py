"""SQLite connection and table setup for student enrollment."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DATABASE_FILE = Path(__file__).resolve().parent.parent / "students.db"


@contextmanager
def database_connection() -> Iterator[sqlite3.Connection]:
    """Open a connection, commit successful work, and roll back errors."""

    connection = sqlite3.connect(DATABASE_FILE, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    """Create the tables required by the enrollment system."""

    with database_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_number TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK (age >= 0),
                email TEXT NOT NULL UNIQUE
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        }

        if "student_number" not in columns:
            connection.execute(
                "ALTER TABLE students ADD COLUMN student_number TEXT"
            )
            connection.execute("""
                UPDATE students
                SET student_number = 'LEGACY-' || id
                WHERE student_number IS NULL
            """)

        if "email" not in columns:
            connection.execute(
                "ALTER TABLE students ADD COLUMN email TEXT"
            )
            connection.execute("""
                UPDATE students
                SET email = 'student' || id || '@example.invalid'
                WHERE email IS NULL
            """)

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_students_student_number
            ON students(student_number)
        """)
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_students_email
            ON students(email)
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT NOT NULL UNIQUE,
                course_name TEXT NOT NULL,
                description TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT NOT NULL UNIQUE,
                subject_name TEXT NOT NULL,
                capacity INTEGER NOT NULL DEFAULT 30
                    CHECK (capacity > 0),
                course_id INTEGER NOT NULL,
                FOREIGN KEY (course_id)
                    REFERENCES courses(id) ON DELETE RESTRICT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                enrollment_date TEXT NOT NULL DEFAULT (DATE('now')),
                status TEXT NOT NULL DEFAULT 'enrolled'
                    CHECK (status IN ('enrolled', 'cancelled')),
                FOREIGN KEY (student_id)
                    REFERENCES students(id) ON DELETE RESTRICT,
                FOREIGN KEY (subject_id)
                    REFERENCES subjects(id) ON DELETE RESTRICT,
                UNIQUE (student_id, subject_id)
            )
        """)