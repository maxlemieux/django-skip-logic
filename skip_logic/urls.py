"""
django-skip-logic urls.py
"""
#from django.conf import settings
from django.conf.urls import url
#from django.conf.urls.static import static

from . import views

app_name = 'skip_logic'
urlpatterns = [
    url(r'^$',
        views.HomeIndexView.as_view(), name='home_index'),
    # Referral codes
    url(r'^(?P<ref_code>[A-Za-z\d]+)$',
        views.process_referral, name='process_referral'),
    # Rewards available
    url(r'^rewards/$',
        views.RewardsIndexView.as_view(), name='rewards'),
    # User Profile
    url(r'^user/(?P<username>\w+)/$',
        views.UserProfileView.as_view(), name='user'),
    # Survey index
    url(r'^surveys/$',
        views.survey_index, name='survey_index'),
    # Survey creation
    url(r'^surveys/new/$',
        views.survey_new, name='survey_new'),
    # Survey detail
    url(r'^surveys/(?P<survey_slug>[0-9A-Za-z]+)/detail/$',
        views.survey_detail, name='survey_detail'),
    # Survey edit
    url(r'^surveys/(?P<survey_slug>[0-9A-Za-z]+)/edit/$',
        views.survey_edit, name='survey_edit'),
    # Survey Delete
    url(r'^surveys/(?P<survey_slug>[0-9A-Za-z]+)/remove/$',
        views.survey_delete, name='survey_delete'),
    # Page detail
    url(r'^surveys/page/(?P<page_slug>[0-9A-Za-z]+)/detail/$',
        views.page_detail, name='page_detail'),
    # Page creation
    url(r'^surveys/(?P<survey_slug>[0-9A-Za-z]+)/page/new/$',
        views.page_new, name='page_new'),
    # Page edit
    url(r'^surveys/page/(?P<page_slug>[0-9A-Za-z]+)/edit/$',
        views.page_edit, name='page_edit'),
    # Page Delete
    url(r'^surveys/page/(?P<page_slug>[0-9A-Za-z]+)/remove/$',
        views.page_delete, name='page_delete'),
    # Question detail
    url(r'^surveys/page/question/(?P<question_slug>[0-9A-Za-z]+)/detail/$',
        views.question_detail, name='question_detail'),
    # Question creation
    url(r'^surveys/page/(?P<page_slug>[0-9A-Za-z]+)/question/new/$',
        views.question_new, name='question_new'),
    # Question edit
    url(r'^surveys/page/question/(?P<question_slug>[0-9A-Za-z]+)/edit/$',
        views.question_edit, name='question_edit'),
    # Question Delete
    url(r'^surveys/page/question/(?P<question_slug>[0-9A-Za-z]+)/remove/$',
        views.question_delete, name='question_delete'),
    # Choice detail
    url(r'^surveys/page/question/choice/(?P<choice_slug>[0-9A-Za-z]+)/detail/$',
        views.choice_detail, name='choice_detail'),
    # Choice creation
    url(r'^surveys/page/question/(?P<question_slug>[0-9A-Za-z]+)/choice/new/$',
        views.choice_new, name='choice_new'),
    # Choice edit
    url(r'^surveys/page/question/choice/(?P<choice_slug>[0-9A-Za-z]+)/edit/$',
        views.choice_edit, name='choice_edit'),
    # Choice Delete
    url(r'^surveys/page/question/choice/(?P<choice_slug>[0-9A-Za-z]+)/remove/$',
        views.choice_delete, name='choice_delete'),
    # Create Yes and No Choices
    url(r'^surveys/page/question/(?P<question_id>[0-9A-Za-z]+)/create_yes_and_no_choices/$',
        views.create_yes_and_no_choices, name='create_yes_and_no_choices'),
    # Path creation
    url(r'^surveys/page/question/choice/(?P<origin_choice_slug>[0-9A-Za-z]+)/path/new/$',
        views.path_new, name='path_new'),
    # Path creation (Page Path)
    url(r'^surveys/page/(?P<origin_page_slug>[0-9A-Za-z]+)/path/new/$',
        views.path_new, name='path_new_pagepath'),
    # Path detail
    url(r'^surveys/page/question/choice/path/(?P<path_slug>[0-9A-Za-z]+)/detail/$',
        views.path_detail, name='path_detail'),
    # Path detail (Page Path)
    url(r'^surveys/page/path/(?P<path_slug>[0-9A-Za-z]+)/detail/$',
        views.path_detail, name='path_detail_pagepath'),
    # Path edit
    url(r'^surveys/page/question/choice/path/(?P<path_slug>[0-9A-Za-z]+)/edit/$',
        views.path_edit, name='path_edit'),
    # Path Delete
    url(r'^surveys/page/question/choice/path/(?P<path_slug>[0-9A-Za-z]+)/remove/$',
        views.path_delete, name='path_delete'),
#    url(r'^surveys/page/question/choice/path/(?P<path_id>[0-9]+)/remove/$',
#        views.path_delete, name='path_delete'),
    # Survey taking
    url(r'^surveys/(?P<survey_slug>[0-9A-Za-z]+)/page/(?P<page_slug>[0-9A-Za-z]+)/$',
        views.PageView.as_view(), name='page'),
    # Call to Action
    url(r'^surveys/(?P<survey_slug>[0-9A-Za-z]+)/completed/$',
        views.CompletedView.as_view(), name='completed'),
    # List of surveys with links to results
    url(r'^surveys/analytics/$',
        views.ResultsView.as_view(), name='results_index'),
    # QuestionResults, per survey
    url(r'^surveys/analytics/(?P<survey_slug>[0-9A-Za-z]+)/$',
        views.SurveyResultsView.as_view(), name='survey_results'),
    # Generate survey results PDF
    url(r'^surveys/analytics/(?P<survey_slug>[0-9A-Za-z]+)/pdf/$',
        views.generate_survey_results_pdf, name='results_pdf'),
    # Vote
    url(r'^(?P<page_slug>[0-9A-Za-z]+)/vote/$',
        views.vote, name='vote'),
    # Campaign list
    url(r'^campaign/$',
        views.campaign_index, name='campaign_index'),
    # Campaign details
    url(r'^campaign/(?P<campaign_id>\d+)/detail/$',
        views.campaign_detail, name='campaign_detail'),
    # Referral code list
    url(r'^campaign/(?P<campaign_id>\d+)/detail/referral_codes/$',
        views.campaign_referral_codes, name='campaign_referral_codes'),
    # Campaign Create
    url(r'^campaign/create/$',
        views.campaign_create, name='campaign_create'),
    # Campaign Delete
    url(r'^campaign/(?P<campaign_id>[0-9]+)/end/$',
        views.campaign_delete, name='campaign_delete'),
    # Sankey JSON
    url(r'^sankey/(?P<survey_slug>[0-9A-Za-z]+)\.json$',
        views.sankey_json, name='sankey_json'),
]
