"""
Views for django-skip-logic. Handles surveys, survey results, call to action.
"""

import random
import string

from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from skip_logic.models import Survey, Page, Path, Choice

from skip_logic.forms import PathForm


def path_detail(request, path_slug):
    """Detail of path object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    path = get_object_or_404(Path, slug=path_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == path.choice.question.page.survey.author:
        return render(request,
                      'skip_logic/path_detail.html',
                      {'path': path, 'my_surveys': my_surveys})
    return Http404("Page not found")



def path_new(request, choice_slug):
    """Create a new path."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    choice = get_object_or_404(Choice, slug=choice_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == choice.question.page.survey.author:
        if request.method == "POST":
            form = PathForm(request.POST)
            if form.is_valid():
                path = form.save(commit=False)
                path.choice = choice
                try:
                    path.save()
                except IntegrityError:
                    messages.add_message(request,
                                         messages.INFO,
                                         "A path for this choice already exists.",)
                    return render(request,
                                  'skip_logic/path_edit.html',
                                  {'form': form, 'path': path, 'my_surveys': my_surveys})
                messages.add_message(request, messages.INFO, "Created new path.",)
                return redirect('skip_logic:path_detail', path_slug=path.slug)
        else:
            new_slug = ''.join(random.choice(string.ascii_uppercase +
                                             string.ascii_lowercase +
                                             string.digits) for _ in range(8))
            form = PathForm(initial={'slug': new_slug})
            form.fields['page'].queryset = \
                Page.objects.filter(survey=choice.question.page.survey).\
                                    exclude(id=choice.question.page.id)
        return render(request,
                      'skip_logic/path_edit.html',
                      {'form': form, 'choice': choice, 'my_surveys': my_surveys})
    else:
        return Http404("Page not found")



def path_edit(request, path_slug):
    """Edit path object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    path = get_object_or_404(Path, slug=path_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == path.choice.question.page.survey.author:
        if request.method == "POST":
            form = PathForm(request.POST, instance=path)
            if form.is_valid():
                path = form.save(commit=False)
                path.save()
                messages.add_message(request, messages.INFO, "Saved changes to path.")
                return redirect('skip_logic:path_detail', path_slug=path.slug)
        else:
            form = PathForm(instance=path)
            form.fields['page'].queryset = \
                Page.objects.filter(survey=path.choice.question.page.survey).\
                             exclude(id=path.choice.question.page.id)
        return render(request,
                      'skip_logic/path_edit.html',
                      {'form': form, 'path': path, 'my_surveys': my_surveys})
    else:
        return Http404("Page not found")



def path_delete(request, path_slug):
    """Delete path object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    path = get_object_or_404(Path, slug=path_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == path.choice.question.page.survey.author:
        if request.method == 'GET':
            # Are you sure?
            return render(request,
                          'skip_logic/path_delete.html',
                          {'path': path, 'my_surveys': my_surveys})
        elif request.method == 'POST':
            # Then let's delete the path
            path.delete()
            messages.add_message(request, messages.INFO, "Removed path.")
            return redirect('skip_logic:choice_detail', choice_slug=path.choice.slug)
    else:
        return Http404("Page not found")
