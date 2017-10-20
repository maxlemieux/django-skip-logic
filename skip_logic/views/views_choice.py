"""
Views for django-skip-logic. Handles surveys, survey results, call to action.
"""

import random
import string

from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from skip_logic.models import Survey, Question, Choice

from skip_logic.forms import ChoiceForm
from skip_logic.views.views_core import random_slug


def get_new_choice_number(question):
    """Gets a new choice number. Used when creating new choices."""
    if Choice.objects.filter(question=question).count() > 0:
        latest_choice_number = Choice.objects.filter(question=question).\
                                                     latest('choice_number').choice_number
        new_choice_number = int(latest_choice_number) + 1
    else:
        new_choice_number = 1
    return new_choice_number



def choice_detail(request, choice_slug):
    """Detail of choice object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    choice = get_object_or_404(Choice, slug=choice_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == choice.question.page.survey.author:
        return render(request,
                      'skip_logic/choice_detail.html',
                      {'choice': choice, 'my_surveys': my_surveys})
    return Http404("Page not found")



def choice_new(request, question_slug):
    """Create a new choice."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    question = get_object_or_404(Question, slug=question_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == question.page.survey.author:
        if request.method == "POST":
            form = ChoiceForm(request.POST, request.FILES)
            if form.is_valid():
                choice = form.save(commit=False)
                if request.POST.get('choice_image', False):
                    choice.choice_image = request.FILES['choice_image']
                choice.question = question
                choice.slug = ''.join(random.choice(string.ascii_uppercase +
                                                    string.ascii_lowercase +
                                                    string.digits) for _ in range(8))
                try:
                    choice.save()
                except IntegrityError:
                    messages.add_message(request, messages.INFO,
                                         """A choice with that choice number already exists.
                                         Please choose a different choice number.""",)

                    return render(request, 'skip_logic/choice_edit.html',
                                  {'form': form, 'choice': choice, 'my_surveys': my_surveys})

                messages.add_message(request, messages.INFO,
                                     "Created new choice " + str(choice.choice_text) +
                                     " for question " + str(question.question_text),)
                return redirect('skip_logic:choice_detail', choice_slug=choice.slug)
        else:
            new_slug = ''.join(random.choice(string.ascii_uppercase +
                                             string.ascii_lowercase +
                                             string.digits) for _ in range(8))
            if Choice.objects.filter(question=question).count() > 0:
                new_choice_number = Choice.objects.filter(question=question).\
                                                       latest('choice_number').choice_number + 1
            else:
                new_choice_number = 1
            form = ChoiceForm(initial={'choice_number': new_choice_number, 'slug': new_slug})
        return render(request, 'skip_logic/choice_edit.html',
                      {'form': form, 'question': question, 'my_surveys': my_surveys})
    else:
        return Http404("Page not found")



def choice_edit(request, choice_slug):
    """Edit choice object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    choice = get_object_or_404(Choice, slug=choice_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == choice.question.page.survey.author:
        if request.method == "POST":
            form = ChoiceForm(request.POST, request.FILES, instance=choice)
            if form.is_valid():
                choice = form.save(commit=False)
                if request.POST.get('choice_image', False):
                    choice.choice_image = request.FILES['choice_image']
                choice.save()
                messages.add_message(request, messages.INFO,
                                     "Saved changes to choice " +
                                     choice.choice_text,)
                return redirect('skip_logic:choice_detail', choice_slug=choice.slug)
        else:
            form = ChoiceForm(instance=choice)
        return render(request, 'skip_logic/choice_edit.html',
                      {'form': form, 'choice': choice, 'my_surveys': my_surveys})
    else:
        return Http404("Page not found")


def choice_delete(request, choice_slug):
    """Delete choice object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    choice = get_object_or_404(Choice, slug=choice_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == choice.question.page.survey.author:
        if request.method == 'GET':
            # Are you sure?
            return render(request, 'skip_logic/choice_delete.html',
                          {'choice': choice, 'my_surveys': my_surveys})
        elif request.method == 'POST':
            # Then let's delete the choice
            question_slug = choice.question.slug
            choice.delete()
            messages.add_message(request, messages.INFO, "Removed choice.")
            return redirect('skip_logic:question_detail', question_slug=question_slug)
    else:
        return Http404("Page not found")


def create_yes_and_no_choices(request, question_id):
    """Create a Yes choice and a No choice for the question."""
    question = Question.objects.get(id=question_id)
    yes_choice = Choice.objects.create(question = question,
                                       choice_text = 'Yes',
                                       choice_number = get_new_choice_number(question),
                                       slug = random_slug(8))
    no_choice = Choice.objects.create(question = question,
                                      choice_text = 'No',
                                      choice_number = get_new_choice_number(question),
                                      slug = random_slug(8))
    messages.add_message(request, messages.INFO,
                         "Created new Yes and No choices for question " + str(question.question_text),)
    return redirect('skip_logic:question_detail', question_slug=question.slug)
