
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.urls import reverse
from django.views import generic
import logging

from .models import Course, Enrollment, Question, Choice, Submission

# Get an instance of a logger
logger = logging.getLogger(__name__)


# User registration
def registration_request(request):
    context = {}

    if request.method == 'GET':
        return render(
            request,
            'onlinecourse/user_registration_bootstrap.html',
            context
        )

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        user_exist = User.objects.filter(username=username).exists()

        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect('onlinecourse:index')

        context['message'] = 'User already exists.'

        return render(
            request,
            'onlinecourse/user_registration_bootstrap.html',
            context
        )


# User login
def login_request(request):
    context = {}

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')

        context['message'] = 'Invalid username or password.'

        return render(
            request,
            'onlinecourse/user_login_bootstrap.html',
            context
        )

    return render(
        request,
        'onlinecourse/user_login_bootstrap.html',
        context
    )


# User logout
def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


# Check whether a user is enrolled in a course
def check_if_enrolled(user, course):
    if user.is_authenticated:
        return Enrollment.objects.filter(
            user=user,
            course=course
        ).exists()

    return False


# Course list view
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]

        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)

        return courses


# Course detail view
class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


# Enroll in a course
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    if user.is_authenticated:
        is_enrolled = check_if_enrolled(user, course)

        if not is_enrolled:
            Enrollment.objects.create(
                user=user,
                course=course,
                mode='honor'
            )

            course.total_enrollment += 1
            course.save()

    return HttpResponseRedirect(
        reverse(
            viewname='onlinecourse:course_details',
            args=(course.id,)
        )
    )


# Extract selected answers from the exam form
def extract_answers(request):
    submitted_answers = []

    for key in request.POST:
        if key.startswith('choice'):
            for value in request.POST.getlist(key):
                try:
                    submitted_answers.append(int(value))
                except (ValueError, TypeError):
                    pass

    return submitted_answers


# Submit an exam
def submit(request, course_id):
    if not request.user.is_authenticated:
        return redirect('onlinecourse:login')

    course = get_object_or_404(Course, pk=course_id)

    if request.method != 'POST':
        return HttpResponseRedirect(
            reverse(
                'onlinecourse:course_details',
                args=(course.id,)
            )
        )

    # Get the user's enrollment
    enrollment = Enrollment.objects.filter(
        user=request.user,
        course=course
    ).first()

    # Create an enrollment if one does not exist
    if enrollment is None:
        enrollment = Enrollment.objects.create(
            user=request.user,
            course=course,
            mode='honor'
        )

        course.total_enrollment += 1
        course.save()

    # Create a submission record
    submission = Submission.objects.create(
        enrollment=enrollment
    )

    # Collect selected choices for this course only
    selected_choice_ids = extract_answers(request)

    valid_choices = Choice.objects.filter(
        id__in=selected_choice_ids,
        question__course=course
    )

    # Save selected choices to the submission
    submission.choices.set(valid_choices)

    # Redirect to the result page
    return redirect(
        'onlinecourse:show_exam_result',
        course_id=course.id,
        submission_id=submission.id
    )


# Display exam results
def show_exam_result(request, course_id, submission_id):
    if not request.user.is_authenticated:
        return redirect('onlinecourse:login')

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    submission = get_object_or_404(
        Submission,
        pk=submission_id
    )

    # Verify submission ownership
    if (
        submission.enrollment.user != request.user
        or submission.enrollment.course != course
    ):
        return HttpResponseForbidden(
            'You are not authorized to view this exam result.'
        )

    # Get selected choices
    selected_choices = submission.choices.all()

    selected_ids = list(
        selected_choices.values_list('id', flat=True)
    )

    # Calculate marks earned and maximum possible marks
    grade = 0
    possible = 0

    for question in course.question_set.all():
        possible += question.grade

        if question.is_get_score(selected_ids):
            grade += question.grade

    # Calculate percentage
    percentage = (
        (grade / possible) * 100
        if possible > 0
        else 0
    )

    # Passing threshold: 80%
    passed = percentage >= 80

    # Context passed to exam_result_bootstrap.html
    context = {
        'course': course,
        'submission': submission,
        'grade': grade,
        'possible': possible,
        'score': grade,
        'total_score': possible,
        'percentage': round(percentage, 1),
        'passed': passed,
        'selected_choices': selected_choices,
    }

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        context
    )
