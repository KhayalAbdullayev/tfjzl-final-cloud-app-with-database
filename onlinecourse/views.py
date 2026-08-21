def extract_selected_choices(request):
    selected_choices = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            selected_choices.append(int(value))
    return selected_choices


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    if not user.is_authenticated:
        return redirect('onlinecourse:login')

    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    
    selected_choice_ids = extract_selected_choices(request)
    for choice_id in selected_choice_ids:
        choice = get_object_or_404(Choice, pk=choice_id)
        submission.choices.add(choice)
    submission.save()

    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_choices = submission.choices.all()
    selected_ids = [choice.id for choice in selected_choices]
    
    total_score = 0
    for question in course.question_set.all():
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    context['course'] = course
    context['grade'] = total_score
    context['submission'] = submission
    context['selected_ids'] = selected_ids
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
