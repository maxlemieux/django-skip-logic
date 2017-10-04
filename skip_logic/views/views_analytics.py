"""
Views for django-skip-logic. Handles surveys, survey results, call to action.
"""

import json


from reportlab.pdfgen import canvas

from django.db.models.functions import Length
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views import generic
from django.contrib.auth.mixins import UserPassesTestMixin

from skip_logic.models import Survey, Page, Question, Path, Choice
from skip_logic.models import QuestionResult


def sankey_json(survey_id):
    """Show a JSON response for the Sankey diagram charts."""
    data = build_sankey(survey_id)
    return HttpResponse(json.dumps(data), content_type='application/json')


class ResultsView(UserPassesTestMixin, generic.TemplateView): # pylint: disable=too-many-ancestors
    """
    This view shows statistics about the survey results.
    Results View is accessible from "Analytics" button in header,
    only for users with Create Survey permissions.
    """
    template_name = 'skip_logic/results_index.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Survey Creators').exists()

    def get_context_data(self, **kwargs):
        """
        Count the unique session IDs for results for this survey.
        Store the count under the key of the survey object.
        """
        context = super().get_context_data(**kwargs)
        context['survey_list'] = Survey.objects.\
            filter(author=self.request.user).order_by('pub_date')
        context['respondent_count_dict'] = {}
        for each_survey in context['survey_list']:
            # Order of transformations: QuerySet => List => Set => Length.
            respondent_count = len(
                set(
                    QuestionResult.objects.filter(
                        question__page__survey=each_survey
                    )
                    .values_list('session')
                )
            )
            context['respondent_count_dict'][each_survey] = respondent_count
        return context


class SurveyResultsView(UserPassesTestMixin, generic.TemplateView): # pylint: disable=too-many-ancestors
    """Get related choices and answers."""

    template_name = 'skip_logic/results_survey_detail.html'

    def test_func(self):
        return self.request.user.groups.filter(name='Survey Creators').exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey_list'] = Survey.objects.\
            filter(author=self.request.user).order_by('pub_date')
        context['respondent_count_dict'] = {}
        for each_survey in context['survey_list']:
            # Order of transformations: QuerySet => List => Set => Length.
            respondent_count = len(
                set(
                    QuestionResult.objects.filter(
                        question__page__survey=each_survey
                    )
                    .values_list('session')
                )
            )
            context['respondent_count_dict'][each_survey] = respondent_count

        context['survey'] = Survey.objects.get(slug=self.kwargs['survey_slug'])
        context['question_list'] = Question.objects.filter(page__survey__slug=self.kwargs['survey_slug'])

        # Call function...too much to inline here
        context['answer_dict'] = build_survey_results(self.kwargs['survey_slug'])

        return context


def build_survey_results(survey_slug):
    """Helper function to make a dictionary of survey results."""
#    survey = Survey.objects.get(slug=survey_slug)
    question_list = Question.objects.annotate(text_len=Length('question_text')).\
                                     filter(page__survey__slug=survey_slug, text_len__gt=0)

    answer_dict = {}
    for this_question in question_list:
        question_choices = Choice.objects.filter(question=this_question)
        question_answers = QuestionResult.objects.\
            filter(question=this_question).order_by('-result_date')
        answer_dict[this_question] = []
        for this_choice in question_choices:
            choice_input_text_list = question_answers.\
                filter(result_object=this_choice).values_list('input_text',
                                                              'result_date',
                                                              'session',
                                                              'username',
                                                              'user_ip_address',
                                                             )
            choice_count = question_answers.filter(result_object=this_choice).count()
            answer_dict[this_question].\
                append([
                    this_choice.choice_text,
                    choice_count,
                    choice_input_text_list,
                ])

    return answer_dict


def build_sankey(survey_id):
    """Helper function to build a dictionary for Sankey charts."""
    page_list = Page.objects.filter(survey=survey_id)

    answer_dict = {}
    answer_dict['nodes'] = []
    answer_dict['links'] = []

    # relation between node number and page ID
    page_node = {}

    node_number = 0
    for this_page in page_list:
        # Add the page to the lookup dict
        page_node[this_page.id] = node_number
        node_number += 1

    node_number = 0
    for this_page in page_list:
        question_answers = QuestionResult.objects.\
            filter(question__page=this_page).order_by('-result_date')
        choice_paths = Path.objects.filter(choice__question__page=this_page)

        answer_dict['nodes'].\
            append({
                "name": this_page.page_text
            })

        for this_path in choice_paths:
            choice_count = question_answers.filter(result_object=this_path.choice).count()
            answer_dict['links'].\
                append({
                    "source": node_number,
                    "target": page_node[this_path.page.id],
                    "value": choice_count
                })

        node_number += 1

    return answer_dict


def generate_survey_results_pdf(request, survey_id):
    """Generates a PDF with the same contents as the survey results detail page."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        raise Http404

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + survey.title + '_results.pdf"'

    # Create the PDF object, using the response object as its "file."
    pdf_obj = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    pdf_obj.drawString(100, 100, "Hello world.")
    pdf_obj.drawString(100, 200, str(timezone.now()))

    # Close the PDF object cleanly, and we're done.
    pdf_obj.showPage()
    pdf_obj.save()
    return response
