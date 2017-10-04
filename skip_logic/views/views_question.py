"""
Views for django-skip-logic question model. Handles questions on page.
"""
import random
import string
from django.db import IntegrityError
#from django.db.models import Max
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from skip_logic.models import Survey, Page, Question
from skip_logic.forms import QuestionForm

def question_detail(request, question_slug):
    """Detail of question object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    question = get_object_or_404(Question, slug=question_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == question.page.survey.author:
        return render(request, 'skip_logic/question_detail.html',
                      {'question': question, 'my_surveys': my_surveys})

    raise Http404("Page not found")



def question_new(request, page_slug):
    """Create new question."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    page = get_object_or_404(Page, slug=page_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == page.survey.author:
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.page = page
                question.slug = ''.join(random.choice(string.ascii_uppercase +
                                                      string.ascii_lowercase +
                                                      string.digits) for _ in range(8))
                try:
                    question.save()
                except IntegrityError:
                    messages.add_message(request, messages.INFO,
                                         """A question with that question number already exists,
                                         please choose a different question number.""",)
                    return render(request, 'skip_logic/question_edit.html',
                                  {'form': form, 'page': page, 'my_surveys': my_surveys})
                messages.add_message(request, messages.INFO,
                                     "Created new question " + question.question_text +
                                     " for page " + page.title,)
                return redirect('skip_logic:question_detail', question_slug=question.slug)
        else:
            new_slug = ''.join(random.choice(string.ascii_uppercase +
                                             string.ascii_lowercase +
                                             string.digits) for _ in range(8))
            if Question.objects.filter(page=page).count() > 0:
                new_question_number = Question.objects.filter(page=page).\
                                                       latest('question_number').question_number + 1
            else:
                new_question_number = 1
            form = QuestionForm(initial={'question_number': new_question_number, 'slug': new_slug})
        return render(request, 'skip_logic/question_edit.html',
                      {'form': form, 'page': page, 'my_surveys': my_surveys})
    else:
        raise Http404("Page not found")



def question_edit(request, question_slug):
    """Edit a question."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    question = get_object_or_404(Question, slug=question_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == question.page.survey.author:
        if request.method == "POST":
            form = QuestionForm(request.POST, instance=question)
            if form.is_valid():
                question = form.save(commit=False)
                question.save()
                messages.add_message(request, messages.INFO,
                                     "Saved changes to question " + question.question_text)
                return redirect('skip_logic:question_detail', question_slug=question.slug)
        else:
            form = QuestionForm(instance=question)
        return render(request, 'skip_logic/question_edit.html',
                      {'form': form, 'question': question, 'my_surveys': my_surveys})
    else:
        return Http404("Page not found")



def question_delete(request, question_slug):
    """Delete question object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    question = get_object_or_404(Question, slug=question_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == question.page.survey.author:
        if request.method == 'GET':
            # Are you sure?
            return render(request, 'skip_logic/question_delete.html',
                          {'question': question, 'my_surveys': my_surveys})
        elif request.method == 'POST':
            # Then let's delete the question
            question.delete()
            messages.add_message(request, messages.INFO,
                                 "Removed question " + question.question_text,)
            return redirect('skip_logic:page_detail', page_slug=question.page.slug)
    else:
        return Http404("Page not found")
