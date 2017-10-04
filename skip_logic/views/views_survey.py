"""
Views for django-skip-logic. Handles surveys, survey results, call to action.
"""
import random
import string
from django.http import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from skip_logic.models import Survey
from skip_logic.forms import SurveyForm

def survey_index(request):
    """Return survey creator's surveys, ordered by date of publication.
    If anon, view published surveys which are available to public."""
    if request.user.is_authenticated:
        latest_survey_list = Survey.objects.filter(
            author=request.user,
        ).order_by('-pub_date')
        my_surveys = Survey.objects.filter(author=request.user).order_by('title')
        return render(request,
                      'skip_logic/survey_index.html',
                      {'latest_survey_list': latest_survey_list, 'my_surveys': my_surveys})

    latest_survey_list = Survey.objects.filter(
        is_public=True,
        pub_date__lte=timezone.now(),
    ).order_by('title')

    return render(request,
                  'skip_logic/survey_index_public.html',
                  {'latest_survey_list': latest_survey_list})


def survey_detail(request, survey_slug):
    """Show details of a survey."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    survey = get_object_or_404(Survey, slug=survey_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == survey.author:
        return render(request,
                      'skip_logic/survey_detail.html',
                      {'survey': survey, 'my_surveys': my_surveys,})
    else:
        raise Http404("Page not found")



def survey_new(request):
    """Create a new survey."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.author = request.user
            survey.save()
            messages.add_message(request, messages.INFO, "Created new survey " + survey.title,)
            return redirect('skip_logic:survey_detail', survey_slug=survey.slug)
    else:
        new_slug = ''.join(random.choice(string.ascii_uppercase +
                                         string.ascii_lowercase +
                                         string.digits) for _ in range(8))
        form = SurveyForm(initial={'slug': new_slug,
                                   'title': "My New Survey"})

    return render(request, 'skip_logic/survey_edit.html', {'form': form, 'my_surveys': my_surveys})



def survey_edit(request, survey_slug):
    """Edit survey object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    survey = get_object_or_404(Survey, slug=survey_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == survey.author:
        if request.method == "POST":
            form = SurveyForm(request.POST, instance=survey)
            if form.is_valid():
                survey = form.save(commit=False)
#            survey.pub_date = timezone.now()
                survey.author = request.user
                survey.save()
                messages.add_message(request, messages.INFO,
                                     "Saved changes to survey " + survey.title,)
                return redirect('skip_logic:survey_detail', survey_slug=survey.slug)
        else:
            form = SurveyForm(instance=survey)
        return render(request,
                      'skip_logic/survey_edit.html',
                      {'form': form, 'survey': survey, 'my_surveys': my_surveys})
    else:
        raise Http404("Page not found")


def survey_delete(request, survey_slug):
    """Delete survey object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    survey = get_object_or_404(Survey, slug=survey_slug)
    my_surveys = Survey.objects.filter(author=request.user).order_by('title')

    if request.user == survey.author:
        if request.method == 'GET':
            # Are you sure?
            return render(request,
                          'skip_logic/survey_delete.html',
                          {'survey': survey, 'my_surveys': my_surveys})
        elif request.method == 'POST':
            # Then let's delete the survey
            survey.delete()
            messages.add_message(request, messages.INFO, "Removed survey " + survey.title,)
            return redirect('skip_logic:survey_index')
    else:
        raise Http404("Page not found")
