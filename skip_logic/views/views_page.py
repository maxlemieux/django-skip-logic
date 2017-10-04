"""
Views for django-skip-logic. Handles surveys, survey results, call to action.
"""

import random
import string

from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages

from skip_logic.models import Survey, Page
from skip_logic.forms import PageForm


def page_detail(request, page_slug):
    """View page details."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    page = get_object_or_404(Page, slug=page_slug)

    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == page.survey.author:
        return render(request, 'skip_logic/page_detail.html',
                      {'page': page, 'my_surveys': my_surveys})
    else:
        raise Http404("Page not found")


def page_new(request, survey_slug):
    """Create a new page."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    survey = get_object_or_404(Survey, slug=survey_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == survey.author:
        if request.method == "POST":
            form = PageForm(request.POST)
            if form.is_valid():
                page = form.save(commit=False)
                page.survey = survey
                page.slug = ''.join(random.choice(string.ascii_uppercase +
                                                  string.ascii_lowercase +
                                                  string.digits) for _ in range(8))
                try:
                    page.save()
                except IntegrityError:
                    messages.add_message(request,
                                         messages.INFO,
                                         """A page with that page number already exists,
                                         please choose a different page number.""",)
                    return render(request,
                                  'skip_logic/page_edit.html',
                                  {'form': form, 'survey': survey, 'my_surveys': my_surveys})

                messages.add_message(request, messages.INFO,
                                     "Created new page " + page.title +
                                     " for survey " + survey.title,)
                return redirect('skip_logic:page_detail', page_slug=page.slug)
        else:
            new_slug = ''.join(random.choice(string.ascii_uppercase +
                                             string.ascii_lowercase +
                                             string.digits) for _ in range(8))
            if Page.objects.filter(survey=survey).count() > 0:
                new_page_number = Page.objects.filter(survey=survey).\
                                               latest('page_number').page_number + 1
            else:
                new_page_number = 1
            form = PageForm(initial={'page_number': new_page_number,
                                     'slug': new_slug,
                                     'title': "My New Page " + str(new_page_number)})
        return render(request, 'skip_logic/page_edit.html',
                      {'form': form, 'survey': survey, 'my_surveys': my_surveys})
    else:
        raise Http404("Page not found")


def page_edit(request, page_slug):
    """Edit a page."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    page = get_object_or_404(Page, slug=page_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == page.survey.author:
        if request.method == "POST":
            form = PageForm(request.POST, instance=page)
            if form.is_valid():
                page = form.save(commit=False)
                page.save()
                messages.add_message(request, messages.INFO,
                                     "Saved changes to page " + page.title,)
                return redirect('skip_logic:page_detail', page_slug=page.slug)
        else:
            form = PageForm(instance=page)
        return render(request, 'skip_logic/page_edit.html',
                      {'form': form, 'page': page, 'my_surveys': my_surveys})
    else:
        return Http404("Page not found")


def page_delete(request, page_slug):
    """Delete page object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    page = get_object_or_404(Page, slug=page_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == page.survey.author:
        if request.method == 'GET':
            # Are you sure?
            return render(request,
                          'skip_logic/page_delete.html',
                          {'page': page, 'my_surveys': my_surveys})
        elif request.method == 'POST':
            # Then let's delete the page
            page.delete()
            messages.add_message(request, messages.INFO,
                                 "Deleted page " + page.page_text,)
            return redirect('skip_logic:survey_detail', survey_slug=page.survey.slug)
    else:
        return Http404("Page not found")
