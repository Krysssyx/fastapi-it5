"""Data models and database operations for the enrollment system."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class StudentInput(BaseModel):
    """Fields accepted when creating or updating a student."""

    name: str = Field(min_length=1)
    age: int = Field(ge=0)
    email: EmailStr


class Student(BaseModel):
    """Student record returned by the API."""

    id: int
    student_number: str
    name: str
    age: int
    email: str

    @staticmethod
    def list_students(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                "SELECT id, student_number, name, age, email "
                "FROM students ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def create_student(student_input, database_connection):
        with database_connection() as connection:
            # Insert with a temporary unique number, then replace it with
            # the real one built from the new row's id so it never collides.
            cursor = connection.execute(
                "INSERT INTO students (student_number, name, age, email) "
                "VALUES (?, ?, ?, ?)",
                (
                    f"TMP-{uuid.uuid4().hex}",
                    student_input.name,
                    student_input.age,
                    student_input.email,
                ),
            )
            student_id = cursor.lastrowid
            student_number = f"{datetime.now().year}-{student_id:04d}"

            connection.execute(
                "UPDATE students SET student_number = ? WHERE id = ?",
                (student_number, student_id),
            )
            row = connection.execute(
                "SELECT id, student_number, name, age, email "
                "FROM students WHERE id = ?",
                (student_id,),
            ).fetchone()
        return dict(row)

    @staticmethod
    def get_student(student_id, database_connection):
        with database_connection() as connection:
            row = connection.execute(
                "SELECT id, student_number, name, age, email "
                "FROM students WHERE id = ?",
                (student_id,),
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def update_student(student_id, student_input, database_connection):
        with database_connection() as connection:
            connection.execute(
                "UPDATE students SET name = ?, age = ?, email = ? "
                "WHERE id = ?",
                (
                    student_input.name,
                    student_input.age,
                    student_input.email,
                    student_id,
                ),
            )
            row = connection.execute(
                "SELECT id, student_number, name, age, email "
                "FROM students WHERE id = ?",
                (student_id,),
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete_student(student_id, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM students WHERE id = ?",
                (student_id,),
            )
            return cursor.rowcount > 0


class CourseInput(BaseModel):
    """Information required to create a course."""

    course_code: str = Field(min_length=1)
    course_name: str = Field(min_length=1)
    description: str | None = None


class Course(BaseModel):
    id: int
    course_code: str
    course_name: str
    description: str | None = None

    @staticmethod
    def create_course(course_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO courses (course_code, course_name, description)
                VALUES (?, ?, ?)
                """,
                (
                    course_input.course_code,
                    course_input.course_name,
                    course_input.description,
                ),
            )
            row = connection.execute(
                "SELECT * FROM courses WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return dict(row)

    @staticmethod
    def list_courses(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM courses ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def update_course(course_id, course_input, database_connection):
        with database_connection() as connection:
            connection.execute(
                """
                UPDATE courses
                SET course_code = ?, course_name = ?, description = ?
                WHERE id = ?
                """,
                (
                    course_input.course_code,
                    course_input.course_name,
                    course_input.description,
                    course_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM courses WHERE id = ?",
                (course_id,),
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete_course(course_id, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM courses WHERE id = ?",
                (course_id,),
            )
            return cursor.rowcount > 0


class SubjectInput(BaseModel):
    """Information required to create a subject."""

    subject_code: str = Field(min_length=1)
    subject_name: str = Field(min_length=1)
    capacity: int = Field(default=30, ge=1)
    course_id: int = Field(gt=0)


class Subject(BaseModel):
    id: int
    subject_code: str
    subject_name: str
    capacity: int
    course_id: int

    @staticmethod
    def create_subject(subject_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO subjects
                    (subject_code, subject_name, capacity, course_id)
                VALUES (?, ?, ?, ?)
                """,
                (
                    subject_input.subject_code,
                    subject_input.subject_name,
                    subject_input.capacity,
                    subject_input.course_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM subjects WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return dict(row)

    @staticmethod
    def list_subjects(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                """
                SELECT subjects.*, courses.course_name
                FROM subjects
                JOIN courses ON subjects.course_id = courses.id
                ORDER BY subjects.id
                """
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def update_subject(subject_id, subject_input, database_connection):
        with database_connection() as connection:
            connection.execute(
                """
                UPDATE subjects
                SET subject_code = ?, subject_name = ?,
                    capacity = ?, course_id = ?
                WHERE id = ?
                """,
                (
                    subject_input.subject_code,
                    subject_input.subject_name,
                    subject_input.capacity,
                    subject_input.course_id,
                    subject_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM subjects WHERE id = ?",
                (subject_id,),
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete_subject(subject_id, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM subjects WHERE id = ?",
                (subject_id,),
            )
            return cursor.rowcount > 0


class EnrollmentInput(BaseModel):
    """Student and subject IDs for an enrollment request."""

    student_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)


class Enrollment(BaseModel):
    id: int
    student_id: int
    subject_id: int
    enrollment_date: str
    status: str

    @staticmethod
    def enroll_student(enrollment_input, database_connection):
        # The connection context commits on success and rolls back
        # if an exception occurs.
        with database_connection() as connection:
            student = connection.execute(
                "SELECT id FROM students WHERE id = ?",
                (enrollment_input.student_id,),
            ).fetchone()

            if not student:
                raise ValueError("Student not found.")

            subject = connection.execute(
                """
                SELECT id, capacity
                FROM subjects
                WHERE id = ?
                """,
                (enrollment_input.subject_id,),
            ).fetchone()

            if not subject:
                raise ValueError("Subject not found.")

            existing = connection.execute(
                """
                SELECT id FROM enrollments
                WHERE student_id = ? AND subject_id = ?
                """,
                (
                    enrollment_input.student_id,
                    enrollment_input.subject_id,
                ),
            ).fetchone()

            if existing:
                raise ValueError(
                    "Student is already registered for this subject."
                )

            enrolled_count = connection.execute(
                """
                SELECT COUNT(*) AS total
                FROM enrollments
                WHERE subject_id = ? AND status = 'enrolled'
                """,
                (enrollment_input.subject_id,),
            ).fetchone()["total"]

            if enrolled_count >= subject["capacity"]:
                raise ValueError("Subject has reached its capacity.")

            cursor = connection.execute(
                """
                INSERT INTO enrollments (student_id, subject_id)
                VALUES (?, ?)
                """,
                (
                    enrollment_input.student_id,
                    enrollment_input.subject_id,
                ),
            )

            row = connection.execute(
                "SELECT * FROM enrollments WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()

        return dict(row)

    @staticmethod
    def list_enrollments(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    enrollments.id,
                    enrollments.student_id,
                    students.name AS student_name,
                    enrollments.subject_id,
                    subjects.subject_name,
                    enrollments.enrollment_date,
                    enrollments.status
                FROM enrollments
                JOIN students ON students.id = enrollments.student_id
                JOIN subjects ON subjects.id = enrollments.subject_id
                ORDER BY enrollments.id
                """
            ).fetchall()

        return [dict(row) for row in rows]

    @staticmethod
    def cancel_enrollment(enrollment_id, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE enrollments
                SET status = 'cancelled'
                WHERE id = ? AND status = 'enrolled'
                """,
                (enrollment_id,),
            )

            if cursor.rowcount == 0:
                return False

        return True