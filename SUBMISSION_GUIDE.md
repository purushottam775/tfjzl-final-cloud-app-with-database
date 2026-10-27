# IBM Skills Network Final Project: Submission Guide

**Project Title:** Add a New Assessment Feature to an Online Course Application  
**Repository:** [https://github.com/dishant1313/tfjzl-final-cloud-app-with-database](https://github.com/dishant1313/tfjzl-final-cloud-app-with-database)  
**Branch:** `main`  
**Target Score:** 15 / 15 (Full Marks)  

---

## Deliverables & Grading Tasks Summary

| Task | Deliverable | Location / Public GitHub URL | Verified Status |
| :--- | :--- | :--- | :--- |
| **Task 1: Models** | GitHub URL to `models.py` | [onlinecourse/models.py](https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/models.py) | ✅ `Question`, `Choice`, `Submission` with `is_get_score` |
| **Task 2: Admin** | GitHub URL to `admin.py` | [onlinecourse/admin.py](https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/admin.py) | ✅ 7 models imported, inlines, and registered |
| **Task 3: Admin Site** | Screenshot of Admin Dashboard | `submission_screenshots/03-admin-site.png` | ✅ Shows Authentication & Authorization and OnlineCourse |
| **Task 4: Course Details**| GitHub URL to template | [templates/onlinecourse/course_details_bootstrap.html](https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/templates/onlinecourse/course_details_bootstrap.html) | ✅ Course lessons + Start Exam collapsible form |
| **Task 5: Views** | GitHub URL to `views.py` | [onlinecourse/views.py](https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/views.py) | ✅ `submit` and `show_exam_result` functions |
| **Task 6: URLs** | GitHub URL to `urls.py` | [onlinecourse/urls.py](https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/urls.py) | ✅ `submit` and `show_exam_result` route paths |
| **Task 7: Final Result**| Screenshot of Exam Result | `submission_screenshots/07-final.png` | ✅ "Congratulations", 100/100 score, question review |

---

## Task Details & Verification

### Task 1 — Models (`onlinecourse/models.py`)
- **Public URL:**  
  `https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/models.py`
- **Key Features Implemented:**
  - `Question`: ForeignKey to `Course`, `question_text = models.CharField(max_length=200)`, `grade = models.IntegerField(default=1)`, optional `lesson`, and `is_get_score(self, selected_ids)`.
  - `is_get_score` ensures that full credit is awarded only when all correct choices and zero incorrect choices are selected. An empty set of choices is handled safely.
  - `Choice`: ForeignKey to `Question`, `choice_text = models.CharField(max_length=100)`, and `is_correct = models.BooleanField(default=False)`.
  - `Submission`: ForeignKey to `Enrollment` and `ManyToManyField(Choice)`. Exact string representation implemented: `f"Submission {self.id} for enrollment {self.enrollment.id}"`.
  - `Enrollment`: Added clean `__str__` returning `f"Enrollment {self.id}"`.

---

### Task 2 — Admin (`onlinecourse/admin.py`)
- **Public URL:**  
  `https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/admin.py`
- **Key Features Implemented:**
  - Imports all 7 required models: `Course`, `Lesson`, `Instructor`, `Learner`, `Question`, `Choice`, and `Submission`.
  - `ChoiceInline`: StackedInline for `Choice` (`extra=2`).
  - `QuestionInline`: StackedInline for `Question` (`extra=2`).
  - `LessonInline`: StackedInline for `Lesson` (`extra=5`).
  - `CourseAdmin`: Configured with `LessonInline` and `QuestionInline`.
  - `LessonAdmin`: Displays `title`.
  - `QuestionAdmin`: Displays `content` and `grade`, with `ChoiceInline`.
  - `SubmissionAdmin`: Displays `enrollment`.
  - Registered all models without duplicate entries.

---

### Task 3 — Admin Site Screenshot
- **File Path:** `submission_screenshots/03-admin-site.png`
- **Confirmation:** Genuine screenshot captured from the running local application. Shows:
  - Header with logged-in user `WELCOME, ADMIN`.
  - **Authentication and Authorization** section (Groups, Users).
  - **OnlineCourse** section (Choices, Courses, Instructors, Learners, Lessons, Questions, Submissions).

---

### Task 4 — Course Details Template
- **Public URL:**  
  `https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/templates/onlinecourse/course_details_bootstrap.html`  
  *(Also mirrored at `https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/templates/onlinecourse/course_detail_bootstrap.html`)*
- **Key Features Implemented:**
  - Preserves course title and lesson loops with full Bootstrap styling.
  - Adds an authenticated learner check (`{% if user.is_authenticated %}`).
  - Includes a "Start Exam" button toggling a Bootstrap collapsible card (`#examCollapse`).
  - Renders all course questions with grade badges.
  - Renders checkbox inputs with unique IDs and names (`choice_{{ choice.id }}`) allowing multiple choice selections per question.
  - Includes CSRF token (`{% csrf_token %}`) and form action targeting `onlinecourse:submit`.
  - Includes a "Submit Exam" button.

---

### Task 5 — Views (`onlinecourse/views.py`)
- **Public URL:**  
  `https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/views.py`
- **Key Features Implemented:**
  - `extract_answers(request)`: Extracts all selected choice IDs from POST parameters matching `choice*`.
  - `submit(request, course_id)`:
    - Enforces authentication and POST method.
    - Retrieves `Course` and verifies/creates user `Enrollment`.
    - Creates a `Submission` instance.
    - Filters and attaches only valid choices belonging to questions in the current course.
    - Redirects to `onlinecourse:show_exam_result`.
  - `show_exam_result(request, course_id, submission_id)`:
    - Enforces authentication.
    - Validates that the requested submission belongs to the current user and course (returns 403 Forbidden on mismatch).
    - Iterates through course questions and evaluates scores using `question.is_get_score(selected_ids)`.
    - Computes total possible score, earned score, percentage, and pass threshold (80%).
    - Renders `onlinecourse/exam_result_bootstrap.html` with full result context.

---

### Task 6 — URLs (`onlinecourse/urls.py`)
- **Public URL:**  
  `https://github.com/dishant1313/tfjzl-final-cloud-app-with-database/blob/main/onlinecourse/urls.py`
- **Routes Added:**
  - `path('<int:course_id>/submit/', views.submit, name='submit')`
  - `path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name='show_exam_result')`

---

### Task 7 — Final Exam Result Screenshot
- **File Path:** `submission_screenshots/07-final.png`
- **Confirmation:** Genuine screenshot captured from an end-to-end user exam flow. Shows:
  - User greeting: `Congratulations, Admin!`.
  - Score badge: `You have passed the exam with a score of 100 / 100 (100.0%)`.
  - "Back to Course" navigation button.
  - "Exam results" section showing Question 1: "Is Django a Python framework" (100 Points).
  - Clear success indicator: `✔ Correct answer selected: Yes` and unselected choice `No`.

---

## All Screenshot Files in Workspace

The `submission_screenshots/` folder contains all 7 required files:
1. `submission_screenshots/01-models.png` — High-resolution code view of Question, Choice, Submission.
2. `submission_screenshots/02-admin-file.png` — Code view of `admin.py` with inlines and registrations.
3. `submission_screenshots/03-admin-site.png` — Real browser capture of Django Admin dashboard.
4. `submission_screenshots/04-course-details.png` — Code view of course detail template with exam markup.
5. `submission_screenshots/05-views.png` — Code view of `submit` and `show_exam_result` views.
6. `submission_screenshots/06-urls.png` — Code view of `urls.py` routes.
7. `submission_screenshots/07-final.png` — Real browser capture of exam pass result with congratulations.

---

## Automated Checks & Test Results

1. **Django System Check:**
   ```bash
   python manage.py check
   # Output: System check identified no issues (0 silenced).
   ```

2. **Migration Dry Run:**
   ```bash
   python manage.py makemigrations --check --dry-run
   # Output: No changes detected
   ```

3. **Database Migrations:**
   ```bash
   python manage.py migrate
   # Output: All migrations applied OK (admin, auth, contenttypes, onlinecourse, sessions).
   ```

4. **Automated Unit & Integration Test Suite (`onlinecourse/tests.py`):**
   ```bash
   python manage.py test
   # Ran 7 tests in 8.958s
   # OK
   ```
   - `test_task1_model_definitions_and_str`: Validates `question_text`, `grade` default=1, `choice_text` max_length=100, relationships, and `Submission` `__str__`.
   - `test_task2_admin_registration`: Verification of all 7 registered models in admin.
   - `test_task4_course_detail_template_with_and_without_questions`: Renders course details both with exam questions and without exam questions, ensuring course name and lessons remain visible.
   - `test_task5_task6_successful_exam`: Correct submission, score 100/100, "Congratulations" alert.
   - `test_exam_failure_and_retest`: Incorrect submission, score 0/100, "Failed" alert, re-test link.
   - `test_multiple_choice_scoring`: Multi-choice grading logic (missing choice fails, extra choice fails, exact match passes).
   - `test_security`: Unauthenticated access redirect, cross-user submission prevention (403), cross-course choice isolation.

---

## Instructions to Push to GitHub

To commit and push the project changes to your GitHub fork:

```bash
git add .
git commit -m "Complete IBM final project: assessment feature, models, admin, views, templates, tests, and screenshots"
git push origin main
```
