"""
Views for django-skip-logic. Handles surveys, survey results, call to action.
"""

import random
import string

from ipware.ip import get_ip

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.models import User

from skip_logic.models import Survey, Page, Question, Path
from skip_logic.models import Reward
from skip_logic.models import QuestionResult


def random_slug(slug_size):
    random_slug = ''.join(random.choice(string.ascii_uppercase +
                                 string.ascii_lowercase +
                                 string.digits) for _ in range(slug_size))
    return random_slug


def equality_check(first, second):
    """A skeleton for more complicated checks."""
    return first == second


class UserProfileView(generic.TemplateView):
    """Show information related to the user account."""
    model = User
    template_name = 'skip_logic/userprofile.html'


class HomeIndexView(generic.TemplateView):
    """Show the index page for the survey site."""
    template_name = 'skip_logic/home_index.html'


class RewardsIndexView(generic.TemplateView):
    """Show available rewards."""
    template_name = 'skip_logic/rewards_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['platinum_reward_list'] = Reward.objects.filter(in_store='True', reward_level=1)
        context['gold_reward_list'] = Reward.objects.filter(in_store='True', reward_level=2)
        context['silver_reward_list'] = Reward.objects.filter(in_store='True', reward_level=3)
        return context


class RewardsView(generic.TemplateView):
    """Show a reward detail."""
    model = Reward
    template_name = 'skip_logic/rewards_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reward_list'] = Reward.objects.filter(in_store='True')
        return context


class PageView(generic.TemplateView):
    """Shows survey pages while taking survey."""
    template_name = "skip_logic/page.html"

    def get_context_data(self, **kwargs):
        user_ip_address = get_ip(self.request)
        survey = get_object_or_404(Survey, slug=self.kwargs['survey_slug'])

        if self.request.user == survey.author:
            pass
        else:
            if QuestionResult.objects.\
                filter(question__page=get_object_or_404(Page,
                                                        slug=self.kwargs['page_slug']),
                       user_ip_address=user_ip_address).count() > 0:
                raise Http404
        if not self.request.session.get('has_session'):
            self.request.session['has_session'] = True
        context = super().get_context_data(**kwargs)

        context['page_question_list'] = \
            Question.objects.filter(page__slug=self.kwargs['page_slug'])

        context['page'] = get_object_or_404(Page, slug=self.kwargs['page_slug'])
        context['survey'] = survey

        return context


class CompletedView(generic.TemplateView):
    """
    Call to action template.
    Call to Action button values set in Survey object are displayed here.
    """
    template_name = "skip_logic/completed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed_survey'] = Survey.objects.get(slug=self.kwargs['survey_slug'])
        return context


def vote(request, page_slug):
    """Store a respondent's vote in the database."""
    page = get_object_or_404(Page, slug=page_slug)
    survey = get_object_or_404(Survey, pk=page.survey.id)

    if Question.objects.filter(page__id=page.id).count() > 0:
        counter = 1
        for this_question in Question.objects.filter(page__id=page.id):
            choice_label = "choice" + str(counter)
            selected_choice = this_question.choice_question.get(pk=request.POST[choice_label])
            input_label = "inputfield" + str(counter)
            try:
                input_text = request.POST[input_label]
            except KeyError:
                input_text = ''
            # Create a new QuestionResult object to store the user's answer
            sessionkey = request.session.session_key
            if (request.user == survey.author or QuestionResult.objects.filter(user_ip_address=get_ip(request), question=this_question).count() == 0):
                if request.user.is_authenticated:
                    QuestionResult.objects.create(
                        user=request.user,
                        username=request.user.username,
                        question=this_question,
                        result_object=selected_choice,
                        input_text=input_text,
                        session=sessionkey,
                        user_ip_address=get_ip(request),
                    )
                else:
                    QuestionResult.objects.create(
                        username="anonymous",
                        question=this_question,
                        result_object=selected_choice,
                        input_text=input_text,
                        session=sessionkey,
                        user_ip_address=get_ip(request),
                    )
                    request.session['key_copy'] = sessionkey
            counter = counter + 1
    else:
        selected_choice = None

    # Get path from page or choice.
    # The default is to go to the Call to Action
    if selected_choice == None:
        try:
            path = Path.objects.get(origin_page=page).page.slug
        except:
            return HttpResponseRedirect(reverse('skip_logic:completed', args=(survey.slug,)))
    else:
        try:
            path = Path.objects.get(choice=selected_choice).page.slug
        except Path.DoesNotExist:
            try:
                path = Path.objects.get(origin_page=page).page.slug
            except:
                return HttpResponseRedirect(reverse('skip_logic:completed', args=(survey.slug,)))

#    if request.user.is_authenticated:
#        reward_currency = 5
#        reward_message = "You earned +" + str(reward_currency) + " reward points"
#        request.user.userprofile.receive_currency(reward_currency)
#            messages.add_message(request, messages.INFO, reward_message)

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.

    return HttpResponseRedirect(reverse('skip_logic:page', args=(survey.slug, path)))
