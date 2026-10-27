from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import Course, Lesson, Instructor, Learner, Enrollment, Question, Choice, Submission


class OnlineCourseExamTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testlearner', password='password123', first_name='Test', last_name='Learner')
        self.other_user = User.objects.create_user(username='otherlearner', password='password123', first_name='Other', last_name='Learner')
        self.admin_user = User.objects.create_superuser(username='adminuser', password='password123', email='admin@test.com')

        self.instructor = Instructor.objects.create(user=self.admin_user, full_time=True, total_learners=50)
        self.course = Course.objects.create(
            name='Learning Django',
            description='Django is an extremely popular and fully featured server-side web framework, written in Python',
            pub_date=timezone.now().date(),
            image='course_images/django.png'
        )
        self.course.instructors.add(self.instructor)

        self.lesson = Lesson.objects.create(
            course=self.course,
            title='What is Django',
            order=0,
            content='Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.'
        )

        self.question = Question.objects.create(
            course=self.course,
            question_text='Is Django a Python framework',
            grade=100
        )
        self.choice_yes = Choice.objects.create(question=self.question, choice_text='Yes', is_correct=True)
        self.choice_no = Choice.objects.create(question=self.question, choice_text='No', is_correct=False)

    def test_task1_model_definitions_and_str(self):
        # 1. Question model fields and defaults
        q_default = Question.objects.create(course=self.course, question_text='Default grade question')
        self.assertEqual(q_default.grade, 1)
        self.assertEqual(str(q_default), 'Default grade question')
        self.assertEqual(q_default.course, self.course)
        # Check actual field on model class
        self.assertTrue(hasattr(Question, 'question_text'))
        self.assertEqual(Question._meta.get_field('question_text').max_length, 200)

        # 2. Choice model fields and defaults
        c_default = Choice.objects.create(question=q_default, choice_text='Choice 1')
        self.assertFalse(c_default.is_correct)
        self.assertEqual(c_default.question, q_default)
        self.assertEqual(str(c_default), 'Choice 1')
        self.assertTrue(hasattr(Choice, 'choice_text'))
        self.assertEqual(Choice._meta.get_field('choice_text').max_length, 100)

        # 3. Submission model fields and __str__
        enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        submission = Submission.objects.create(enrollment=enrollment)
        submission.choices.add(c_default)
        expected_str = f"Submission {submission.id} for enrollment {enrollment.id}"
        self.assertEqual(str(submission), expected_str)

        # Check relationships
        self.assertEqual(submission.enrollment, enrollment)
        self.assertIn(c_default, submission.choices.all())

    def test_task2_admin_registration(self):
        from django.contrib import admin
        self.assertIn(Course, admin.site._registry)
        self.assertIn(Lesson, admin.site._registry)
        self.assertIn(Instructor, admin.site._registry)
        self.assertIn(Learner, admin.site._registry)
        self.assertIn(Question, admin.site._registry)
        self.assertIn(Choice, admin.site._registry)
        self.assertIn(Submission, admin.site._registry)

    def test_task4_course_detail_template_with_and_without_questions(self):
        # Case 1: Course containing at least one lesson and one question
        self.client.login(username='testlearner', password='password123')
        response = self.client.get(reverse('onlinecourse:course_details', args=(self.course.id,)))
        self.assertEqual(response.status_code, 200)
        # Verify course name and lesson details remain visible
        self.assertContains(response, 'Learning Django')
        self.assertContains(response, 'What is Django')
        self.assertContains(response, 'Django is a high-level Python web framework')
        # Verify question and choices
        self.assertContains(response, 'Is Django a Python framework')
        self.assertContains(response, 'Yes')
        self.assertContains(response, 'No')
        self.assertContains(response, 'Submit Exam')

        # Case 2: Course containing lessons but NO exam questions
        empty_course = Course.objects.create(
            name='Python Basics Without Exam',
            description='A course without questions'
        )
        Lesson.objects.create(
            course=empty_course,
            title='Introduction to Python',
            order=0,
            content='Python is an easy to learn programming language.'
        )

        response_empty = self.client.get(reverse('onlinecourse:course_details', args=(empty_course.id,)))
        self.assertEqual(response_empty.status_code, 200)
        # Course name and lessons MUST remain visible even without questions
        self.assertContains(response_empty, 'Python Basics Without Exam')
        self.assertContains(response_empty, 'Introduction to Python')
        self.assertContains(response_empty, 'Python is an easy to learn programming language.')
        # Fallback message is displayed
        self.assertContains(response_empty, 'No exam questions available for this course.')

    def test_task5_task6_successful_exam(self):
        self.client.login(username='testlearner', password='password123')
        # Submit correct choice
        response = self.client.post(
            reverse('onlinecourse:submit', args=(self.course.id,)),
            {f'choice_{self.choice_yes.id}': str(self.choice_yes.id)},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Congratulations')
        self.assertContains(response, '100 / 100')
        self.assertContains(response, '100.0%')
        self.assertContains(response, 'Correct answer selected')

        # Verify submission saved
        submission = Submission.objects.filter(enrollment__user=self.user, enrollment__course=self.course).first()
        self.assertIsNotNone(submission)
        self.assertIn(self.choice_yes, submission.choices.all())

    def test_exam_failure_and_retest(self):
        self.client.login(username='testlearner', password='password123')
        # Submit incorrect choice
        response = self.client.post(
            reverse('onlinecourse:submit', args=(self.course.id,)),
            {f'choice_{self.choice_no.id}': str(self.choice_no.id)},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Failed')
        self.assertContains(response, '0 / 100')
        self.assertContains(response, 'Re-test')
        self.assertContains(response, 'Wrong answer selected')

    def test_multiple_choice_scoring(self):
        # Create multi-choice question
        q_multi = Question.objects.create(course=self.course, question_text='Which languages run on Python VM?', grade=50)
        c_py = Choice.objects.create(question=q_multi, choice_text='Python', is_correct=True)
        c_cy = Choice.objects.create(question=q_multi, choice_text='Cython', is_correct=True)
        c_rb = Choice.objects.create(question=q_multi, choice_text='Ruby', is_correct=False)

        # Both correct selected -> True
        self.assertTrue(q_multi.is_get_score([c_py.id, c_cy.id]))
        # Only one correct selected -> False
        self.assertFalse(q_multi.is_get_score([c_py.id]))
        # Both correct plus one incorrect -> False
        self.assertFalse(q_multi.is_get_score([c_py.id, c_cy.id, c_rb.id]))
        # Empty selections -> False
        self.assertFalse(q_multi.is_get_score([]))

        # Question with no correct answers
        q_none = Question.objects.create(course=self.course, question_text='Impossible question', grade=20)
        Choice.objects.create(question=q_none, choice_text='Wrong 1', is_correct=False)
        self.assertFalse(q_none.is_get_score([]))

    def test_security(self):
        # 1. Unauthenticated user cannot submit
        response = self.client.post(
            reverse('onlinecourse:submit', args=(self.course.id,)),
            {f'choice_{self.choice_yes.id}': str(self.choice_yes.id)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('onlinecourse:login'), response.url)

        # 2. One user cannot view another user's submission result
        enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        submission = Submission.objects.create(enrollment=enrollment)
        submission.choices.add(self.choice_yes)

        # Login as other_user and attempt to access testlearner's result
        self.client.login(username='otherlearner', password='password123')
        response = self.client.get(reverse('onlinecourse:show_exam_result', args=(self.course.id, submission.id)))
        self.assertEqual(response.status_code, 403)

        # 3. Choice from another course cannot be attached
        other_course = Course.objects.create(name='Other Course', description='Other')
        other_q = Question.objects.create(course=other_course, question_text='Other question', grade=10)
        other_c = Choice.objects.create(question=other_q, choice_text='Other choice', is_correct=True)

        self.client.login(username='testlearner', password='password123')
        self.client.post(
            reverse('onlinecourse:submit', args=(self.course.id,)),
            {f'choice_{other_c.id}': str(other_c.id), f'choice_{self.choice_yes.id}': str(self.choice_yes.id)}
        )
        latest_sub = Submission.objects.filter(enrollment__user=self.user, enrollment__course=self.course).order_by('-id').first()
        self.assertNotIn(other_c, latest_sub.choices.all())
