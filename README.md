# Student Enrollment Management System API

A REST API built with **FastAPI** & **SQLite**

**Features**

- Manage students, courses, and subjects (create, read, update, delete)
- Student numbers are generated automatically (for example `2026-0001`)
- Enroll a student in a subject, with checks for duplicates and subject capacity
- Cancel an enrollment, which frees the seat in that subject
- Database rules protect your data: you cannot delete a course, subject, or student that is still in use

---

## 1. Requirements

- Python **3.10 or newer** (check with `python --version`, or `py --version` on Windows)
- Git

The packages used are **fastapi**, **uvicorn**, and **email-validator** (needed to validate student emails). They are all listed in `requirements.txt`.

No database server is needed: SQLite is built into Python.

## 2. Setup

### 2.1 Clone the repository

```bash
git clone https://github.com/Krysssyx/fastapi-it5.git
cd fastapi-it5
```

### 2.2 Create and activate a virtual environment

Run the commands for your system from inside the project folder (the one that contains `main.py`).

**Windows (PowerShell)**

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell refuses to run the activation script, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**macOS / Linux (bash or zsh)**

```bash
python3 -m venv venv
source venv/bin/activate
```

When it works, your prompt starts with `(venv)`.

### 2.3 Install the requirements

```bash
python -m pip install -r requirements.txt
```

### 2.4 Run the application

```bash
uvicorn main:app --reload
```

If the `uvicorn` command is not found, use `python -m uvicorn main:app --reload` instead.

You should see a line like `Uvicorn running on http://127.0.0.1:8000`. Press `Ctrl+C` to stop it.

### 2.5 Open the interactive documentation

Open **http://127.0.0.1:8000/docs** in a browser. This Swagger page lists every endpoint and lets you test them without writing any client code.

### 2.6 The database

The first time the app starts it creates a SQLite file named **`students.db`** next to `main.py` and creates all the tables. Data is kept between restarts. This file is not uploaded to Git.

To start again from an empty database: stop the server, delete `students.db`, and start the server again. **Do this before section 5**, so the ids in the examples match yours.

---

## 3. Using the API

On the `/docs` page, click an endpoint, press **Try it out**, edit the request body or fill in the parameters, then press **Execute**. The result appears under **Server response**. Errors come back as `{"detail": "..."}` with a message explaining what went wrong.

### All endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/students` | List all students |
| POST | `/student` | Create a student |
| PUT | `/student/{student_id}` | Replace a student's name, age, and email |
| DELETE | `/student/{student_id}` | Delete a student |
| GET | `/courses` | List all courses |
| POST | `/courses` | Create a course |
| PUT | `/courses/{course_id}` | Replace a course |
| DELETE | `/courses/{course_id}` | Delete a course |
| GET | `/subjects` | List all subjects (with their course name) |
| POST | `/subjects` | Create a subject |
| PUT | `/subjects/{subject_id}` | Replace a subject |
| DELETE | `/subjects/{subject_id}` | Delete a subject |
| GET | `/enrollments` | List all enrollments (with student and subject names) |
| POST | `/enrollments` | Enroll a student in a subject |
| PATCH | `/enrollments/{enrollment_id}/cancel` | Cancel an enrollment |

Note that the student endpoints use the singular path `/student`, while courses, subjects, and enrollments use plural paths. Only `GET /students` (plural) lists students.

### Rules to know

- **Student number:** generated automatically from the current year and the student's id, like `2026-0001`. You never type it in.
- **Email:** must be a valid email address and must be unique.
- **Course code and subject code:** must be unique.
- **Subject capacity:** defaults to 30 and must be at least 1. Only enrollments with status `enrolled` count toward it, so cancelling an enrollment frees a seat.
- **One enrollment per student and subject:** a student cannot enroll in the same subject twice, even after cancelling the first enrollment.
- **Cancelling** keeps the enrollment record with status `cancelled`. It is not deleted.
- **Protected deletes:** you cannot delete a course that still has subjects, a subject that has enrollment records, or a student that has enrollment records (cancelled ones count too).

## 4. Project structure

```
main.py                  creates the app and defines all the endpoints
requirements.txt
README.md
app/
    database.py          SQLite connection and table creation
    models.py            Pydantic models and the database operations
```

---

## 5. Sample tests for every endpoint

Do the tests **in order, starting from an empty database** (see 2.6). Part A is the normal flow, Part B the error cases, and Part C the rules that involve several tables.

### Part A: Normal flow

#### A1. Home

`GET /` returns:

```json
{"message": "Welcome to the Student Enrollment Management System!", "docs": "/docs"}
```

#### A2. Courses

**Create** `POST /courses`
```json
{"course_code": "BSIT", "course_name": "BS Information Technology", "description": "Four-year IT program"}
```
The new course comes back with `"id": 1`. Create two more, one at a time:
```json
{"course_code": "BSCS", "course_name": "BS Computer Science"}
```
```json
{"course_code": "TEMP", "course_name": "Temporary Course"}
```
(`description` is optional and comes back as `null` when left out.)

**List** `GET /courses` returns the 3 courses.

**Replace** `PUT /courses/2`
```json
{"course_code": "BSCS", "course_name": "BS Computer Science (Updated)", "description": "Computing and algorithms"}
```

**Delete** `DELETE /courses/3` returns `{"message": "Course deleted successfully"}`. Then `GET /courses` lists only 2 courses.

#### A3. Subjects

**Create** `POST /subjects`
```json
{"subject_code": "IT101", "subject_name": "Intro to Computing", "capacity": 2, "course_id": 1}
```
It comes back with `"id": 1`. Create two more:
```json
{"subject_code": "IT102", "subject_name": "Programming 1", "course_id": 1}
```
The second one comes back with `"capacity": 30` (the default).
```json
{"subject_code": "CS101", "subject_name": "Discrete Math", "capacity": 25, "course_id": 2}
```

**List** `GET /subjects` returns the 3 subjects, each with its `course_name`.

**Replace** `PUT /subjects/3`
```json
{"subject_code": "CS101", "subject_name": "Discrete Mathematics", "capacity": 40, "course_id": 2}
```

**Delete** `DELETE /subjects/3` returns `{"message": "Subject deleted successfully"}`.

#### A4. Students

**Create** `POST /student`
```json
{"name": "Ana Cruz", "age": 19, "email": "ana@school.edu"}
```
It comes back with `"id": 1` and a generated `student_number` such as `2026-0001` (the year is the current year). Create two more:
```json
{"name": "Ben Lim", "age": 20, "email": "ben@school.edu"}
```
```json
{"name": "Carla Reyes", "age": 21, "email": "carla@school.edu"}
```

**List** `GET /students` returns the 3 students.

**Replace** `PUT /student/2`
```json
{"name": "Benjamin Lim", "age": 20, "email": "ben@school.edu"}
```
The student number stays the same; only name, age, and email change.

**Delete** `DELETE /student/3` returns `{"message": "Student deleted successfully"}`. Then `GET /students` lists only 2 students.

#### A5. Enrollments

**Enroll** `POST /enrollments`
```json
{"student_id": 1, "subject_id": 1}
```
It comes back with `"id": 1`, `"status": "enrolled"`, and today's `enrollment_date`. Enroll Ben in the same subject:
```json
{"student_id": 2, "subject_id": 1}
```

**List** `GET /enrollments` returns both enrollments, with `student_name` and `subject_name` included.

**Cancel** `PATCH /enrollments/2/cancel` returns `{"message": "Enrollment cancelled successfully"}`. Check `GET /enrollments`: enrollment 2 now shows `"status": "cancelled"`, and it is still listed.

---

### Part B: Error cases to try

Run these after Part A. Each request should be rejected as shown. A `422` means the request body or parameters were invalid, `404` means not found, and `409` means a conflict with existing data.

#### Students

Use this body as the base: `{"name": "Test", "age": 18, "email": "test@school.edu"}`

| Request | Change | Result |
|---|---|---|
| `POST /student` | `"email": "ana@school.edu"` | 409 "Student already exists (duplicate email) or violates a constraint" |
| `POST /student` | `"name": ""` | 422 (name must not be empty) |
| `POST /student` | `"age": -1` | 422 (age must be 0 or more) |
| `POST /student` | `"email": "not-an-email"` | 422 (invalid email) |
| `POST /student` | `{}` | 422 (all fields are required) |
| `PUT /student/{id}` | `99` with the base body | 404 "Student not found" |
| `PUT /student/{id}` | `2` with `{"name": "Ben", "age": 20, "email": "ana@school.edu"}` | 409 "Email already in use" |
| `DELETE /student/{id}` | `99` | 404 "Student not found" |
| `DELETE /student/{id}` | `1` | 409 "Cannot delete a student with enrollment records" (Ana is enrolled) |

#### Courses

Use this body as the base: `{"course_code": "TEST", "course_name": "Test Course"}`

| Request | Change | Result |
|---|---|---|
| `POST /courses` | `"course_code": "BSIT"` | 409 "Course code already exists" |
| `POST /courses` | `"course_code": ""` | 422 |
| `POST /courses` | remove `course_name` | 422 (required) |
| `PUT /courses/{id}` | `99` with the base body | 404 "Course not found" |
| `PUT /courses/{id}` | `2` with `"course_code": "BSIT"` | 409 "Course code already exists" |
| `DELETE /courses/{id}` | `99` | 404 "Course not found" |
| `DELETE /courses/{id}` | `1` | 409 "Cannot delete a course that still has subjects" |

#### Subjects

Use this body as the base: `{"subject_code": "TEST1", "subject_name": "Test Subject", "course_id": 1}`

| Request | Change | Result |
|---|---|---|
| `POST /subjects` | `"subject_code": "IT101"` | 409 "Subject code already exists or course is invalid" |
| `POST /subjects` | `"course_id": 99` | 409 "Subject code already exists or course is invalid" (course does not exist) |
| `POST /subjects` | `"capacity": 0` | 422 (capacity must be at least 1) |
| `POST /subjects` | `"course_id": 0` | 422 (must be greater than 0) |
| `PUT /subjects/{id}` | `99` with the base body | 404 "Subject not found" |
| `PUT /subjects/{id}` | `2` with `"subject_code": "IT101"` | 409 "Subject code already exists or course is invalid" |
| `DELETE /subjects/{id}` | `99` | 404 "Subject not found" |
| `DELETE /subjects/{id}` | `1` | 409 "Cannot delete a subject with enrollment records" |

#### Enrollments

| Request | Body / parameter | Result |
|---|---|---|
| `POST /enrollments` | `{"student_id": 99, "subject_id": 1}` | 404 "Student not found." |
| `POST /enrollments` | `{"student_id": 1, "subject_id": 99}` | 404 "Subject not found." |
| `POST /enrollments` | `{"student_id": 0, "subject_id": 1}` | 422 (ids must be greater than 0) |
| `POST /enrollments` | `{"student_id": 1, "subject_id": 1}` | 409 "Student is already registered for this subject." |
| `PATCH /enrollments/{id}/cancel` | `99` | 404 "Enrollment not found or already cancelled" |
| `PATCH /enrollments/{id}/cancel` | `2` (already cancelled) | 404 "Enrollment not found or already cancelled" |

---

### Part C: Rules that involve several tables

Run these after Part B, in order.

#### C1. A full subject refuses new students

Subject 1 (`IT101`) has a capacity of 2. Ana is enrolled and Ben's enrollment was cancelled, so one seat is taken. Create two more students:

`POST /student`
```json
{"name": "Dan Uy", "age": 22, "email": "dan@school.edu"}
```
```json
{"name": "Eva Tan", "age": 18, "email": "eva@school.edu"}
```
They come back with ids 4 and 5 (id 3 was deleted and is not reused).

Enroll Dan: `POST /enrollments` with `{"student_id": 4, "subject_id": 1}` works. The subject now has 2 enrolled students, which is its capacity.

Now enroll Eva: `POST /enrollments` with `{"student_id": 5, "subject_id": 1}` is refused with **409 "Subject has reached its capacity."**

#### C2. Cancelling frees a seat

`PATCH /enrollments/1/cancel` cancels Ana's enrollment. Now repeat the request for Eva: `POST /enrollments` with `{"student_id": 5, "subject_id": 1}` **works**, because only enrolled students count toward capacity.

Check `GET /enrollments`: it lists Ana (cancelled), Ben (cancelled), Dan (enrolled), and Eva (enrolled).

#### C3. Cancelled enrollments still count as records

- `POST /enrollments` with `{"student_id": 2, "subject_id": 1}` is refused with "Student is already registered for this subject." Ben cancelled earlier, but the record still exists, so he cannot enroll again.
- `DELETE /student/1` is refused with "Cannot delete a student with enrollment records", even though Ana's enrollment is cancelled.
- `DELETE /subjects/1` is refused because the subject has enrollment records.
- `DELETE /courses/1` is refused because the course still has subjects.

#### C4. Delete in the right order

To remove a course completely, work from the bottom up. Use a fresh course for this test:

1. `POST /courses` with `{"course_code": "TEST", "course_name": "Test Course"}` (comes back with `"id": 4`).
2. `POST /subjects` with `{"subject_code": "TEST1", "subject_name": "Test Subject", "course_id": 4}` (comes back with `"id": 4`).
3. `DELETE /courses/4` is refused: "Cannot delete a course that still has subjects".
4. `DELETE /subjects/4` works, because nobody is enrolled in it.
5. `DELETE /courses/4` now works.