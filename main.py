"""FastAPI application for the Student Enrollment Management System."""

import sqlite3

from fastapi import FastAPI, HTTPException

from app.database import database_connection, initialize_database
from app.models import (
    Student,
    StudentInput,
    Course,
    CourseInput,
    Subject,
    SubjectInput,
    Enrollment,
    EnrollmentInput,
)

app = FastAPI(title="Student Enrollment Management System")

initialize_database()


@app.get("/")
def home():
    return {
        "message": "Welcome to the Student Enrollment Management System!",
        "docs": "/docs",
    }


@app.get("/students")
def get_students():
    return {
        "students": Student.list_students(
            database_connection=database_connection
        )
    }


@app.post("/student", status_code=201)
def create_student(student: StudentInput):
    try:
        result = Student.create_student(student, database_connection)
        return {"student": result}
    except sqlite3.IntegrityError as error:
        message = str(error)
        print(f"Database integrity error: {message}")

        if "NOT NULL" in message:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required value: {message}",
            )

        raise HTTPException(
            status_code=409,
            detail="Student already exists (duplicate email) "
            "or violates a constraint",
        )


@app.put("/student/{student_id}")
def edit_student(student_id: int, student: StudentInput):
    try:
        result = Student.update_student(
            student_id, student, database_connection
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Email already in use")

    if result is None:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"student": result}


@app.delete("/student/{student_id}")
def delete_student(student_id: int):
    try:
        deleted = Student.delete_student(student_id, database_connection)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a student with enrollment records",
        )

    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"}


@app.post("/courses", status_code=201)
def create_course(course: CourseInput):
    try:
        result = Course.create_course(course, database_connection)
        return {"course": result}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Course code already exists",
        )


@app.get("/courses")
def get_courses():
    return {
        "courses": Course.list_courses(database_connection)
    }


@app.put("/courses/{course_id}")
def edit_course(course_id: int, course: CourseInput):
    try:
        result = Course.update_course(
            course_id, course, database_connection
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Course code already exists",
        )

    if result is None:
        raise HTTPException(status_code=404, detail="Course not found")

    return {"course": result}


@app.delete("/courses/{course_id}")
def delete_course(course_id: int):
    try:
        deleted = Course.delete_course(course_id, database_connection)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a course that still has subjects",
        )

    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found")

    return {"message": "Course deleted successfully"}


@app.post("/subjects", status_code=201)
def create_subject(subject: SubjectInput):
    try:
        result = Subject.create_subject(subject, database_connection)
        return {"subject": result}
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Subject code already exists or course is invalid",
        )


@app.get("/subjects")
def get_subjects():
    return {
        "subjects": Subject.list_subjects(database_connection)
    }


@app.put("/subjects/{subject_id}")
def edit_subject(subject_id: int, subject: SubjectInput):
    try:
        result = Subject.update_subject(
            subject_id, subject, database_connection
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Subject code already exists or course is invalid",
        )

    if result is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    return {"subject": result}


@app.delete("/subjects/{subject_id}")
def delete_subject(subject_id: int):
    try:
        deleted = Subject.delete_subject(subject_id, database_connection)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a subject with enrollment records",
        )

    if not deleted:
        raise HTTPException(status_code=404, detail="Subject not found")

    return {"message": "Subject deleted successfully"}


@app.post("/enrollments", status_code=201)
def create_enrollment(enrollment: EnrollmentInput):
    try:
        result = Enrollment.enroll_student(
            enrollment, database_connection
        )
        return {"enrollment": result}
    except ValueError as error:
        message = str(error)

        if message in ("Student not found.", "Subject not found."):
            raise HTTPException(status_code=404, detail=message)

        raise HTTPException(status_code=409, detail=message)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Enrollment conflicts with an existing record",
        )


@app.get("/enrollments")
def get_enrollments():
    return {
        "enrollments": Enrollment.list_enrollments(database_connection)
    }


@app.patch("/enrollments/{enrollment_id}/cancel")
def cancel_enrollment(enrollment_id: int):
    cancelled = Enrollment.cancel_enrollment(
        enrollment_id, database_connection
    )

    if not cancelled:
        raise HTTPException(
            status_code=404,
            detail="Enrollment not found or already cancelled",
        )

    return {"message": "Enrollment cancelled successfully"}
