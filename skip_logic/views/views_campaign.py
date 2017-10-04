"""
Views for django-skip-logic. Handles surveys, survey results, call to action.
"""

import random
import string

import geoip2.database

from ipware.ip import get_ip

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from skip_logic.models import Campaign, Survey, ReferralCode


def campaign_index(request):
    """Show list of Campaign objects, newest first."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    campaign_list = Campaign.objects.filter(author=request.user).order_by('created_date').reverse()
    context = {
        'campaign_list': campaign_list,
    }

    return render(request, 'skip_logic/campaign_index.html', context)


# campaign_detail accepts two arguments: the normal request object and an integer
# whose value is mapped by campaign_id defined in r'^campaign/(?P<campaign_id>\d+)/detail.html$'
# If it's a POST, it updates the details.
def campaign_detail(request, campaign_id):
    """Detail view for Campaign object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    try:
        campaign = Campaign.objects.get(pk=campaign_id)
    except Campaign.DoesNotExist:
        # If no Post has id campaign_id, we raise an HTTP 404 error.
        raise Http404

    campaign_list = Campaign.objects.filter(author=request.user).order_by('created_date').reverse()

    if request.method == 'GET':
        return render(request, 'skip_logic/campaign_detail.html',
                      {'campaign': campaign, 'campaign_list': campaign_list})
    elif request.method == 'POST':
        campaign.name = request.POST['campaign_name']
        campaign.description = request.POST['campaign_description']
        campaign.save()

        messages.add_message(request, messages.INFO,
                             "Successfully updated campaign " + campaign.name,)
        return HttpResponseRedirect(reverse('skip_logic:campaign_detail',
                                            kwargs={'campaign_id': campaign.id}))


def campaign_create(request):
    """Create new Campaign object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    campaign_list = Campaign.objects.filter(author=request.user).order_by('created_date').reverse()
    context = {
        'campaign_list': campaign_list,
    }

    if request.method == 'GET':
        return render(request, 'skip_logic/campaign_create.html', context)
    elif request.method == 'POST':
        campaign = Campaign.objects.create(name=request.POST['campaign_name'],
                                           description=request.POST['campaign_description'],
                                           author=request.user)
        messages.add_message(request, messages.INFO, "Created campaign " + campaign.name,)
        return HttpResponseRedirect(reverse('skip_logic:campaign_detail',
                                            kwargs={'campaign_id': campaign.id}))



def campaign_delete(request, campaign_id):
    """Delete Campaign object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    try:
        campaign = Campaign.objects.get(pk=campaign_id)
    except Campaign.DoesNotExist:
        raise Http404

    campaign_list = Campaign.objects.filter(author=request.user).order_by('created_date').reverse()
    context = {
        'campaign': campaign,
        'campaign_list': campaign_list,
    }

    if request.method == 'GET':
        # Are you sure?
        return render(request, 'skip_logic/campaign_delete.html', context)
    elif request.method == 'POST':
        # Then let's delete the campaign
        campaign.delete()
        messages.add_message(request, messages.INFO, "Deleted campaign " + campaign.name,)
        return HttpResponseRedirect(reverse('skip_logic:campaign_index'))



def campaign_referral_codes(request, campaign_id):
    """CRU for ReferralCode objects. Deletion is not supported directly.
    Instead, there is a cascading delete from survey object."""
    if request.user.is_authenticated:
        if not request.user.groups.filter(name='Survey Creators').exists():
            raise Http404("Page not found")
    else:
        raise Http404("Page not found")

    # Complete available survey list for context
    surveys = Survey.objects.filter(author=request.user)

    # Campaign for context
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
    except Campaign.DoesNotExist:
        raise Http404

    # List of just the current referral code surveys
    referral_codes_distinct_surveys = ReferralCode.objects.\
        filter(campaign=campaign).\
        distinct('survey')

    if request.method == 'GET':
        # just show the codes
        # Dictionary of referral codes with key == survey.title
        referral_codes = {}
        order_by = request.GET.get('order_by', 'pk')
        for survey in referral_codes_distinct_surveys.values_list('survey__title'):
            referral_codes[survey[0]] = ReferralCode.objects.\
                                                              filter(campaign=campaign,
                                                                     survey__title=survey[0]).\
                                                              order_by(order_by)

        context = {
            'survey_list': surveys,
            'campaign': campaign,
            'referral_codes': referral_codes,
        }

        return render(request, 'skip_logic/campaign_referral_codes.html', context)

    elif request.method == 'POST':
        # create new ReferralCodes, then show the codes
        try:
            survey = Survey.objects.get(pk=request.POST['referral_survey'])
        except Survey.DoesNotExist:
            raise Http404

        count = 0

        if request.POST['referral_code_count'] == "0":
            return render(request, 'skip_logic/campaign_referral_codes.html', context)
        while count < int(request.POST['referral_code_count']) and count < 1000:
            random_string = ''.join(random.choice(string.ascii_uppercase +
                                                  string.ascii_lowercase +
                                                  string.digits) for _ in range(16))
            ReferralCode.objects.create(survey=survey, campaign=campaign, code=random_string)
            count += 1

        messages.add_message(request,
                             messages.INFO,
                             "Created " + request.POST['referral_code_count'] +
                             " codes for survey " + survey.title +
                             " in campaign \"" + campaign.name + "\"",)

        # Dictionary of referral codes with key == survey.title
        new_codes = {}
        for referral_survey in referral_codes_distinct_surveys.values_list('survey__title'):
            new_codes[referral_survey[0]] = ReferralCode.objects.\
                                                         filter(campaign=campaign,
                                                                survey__title=referral_survey[0]).\
                                                         order_by('last_used_date')

        context = {
            'survey_list': surveys,
            'campaign': campaign,
            'referral_codes': new_codes,
        }

        return render(request, 'skip_logic/campaign_referral_codes.html', context)


def process_referral(request, ref_code):
    """Connect referral code to survey."""
    try:
        referral_code = ReferralCode.objects.get(code=ref_code)
    except ReferralCode.DoesNotExist:
        raise Http404


    # Call a model method to save the date
    referral_code.update_last_used_date()

    last_used_ip = get_ip(request)

    if last_used_ip is not None:
        # Save the IP address
        referral_code.last_ip = last_used_ip

        geodb = '/home/dslapp/django-skip-logic-PROJECT/django_skip_logic/static/GeoLite2-City.mmdb'
        reader = geoip2.database.Reader(geodb)
        response = reader.city(last_used_ip)
        country = response.country.name
        state = response.subdivisions.most_specific.name
        city = response.city.name
        postal_code = response.postal.code # pylint: disable=no-member
        reader.close()

        referral_code.geoip_city = city
        referral_code.geoip_state = state
        referral_code.geoip_postal_code = postal_code
        referral_code.geoip_country = country

        referral_code.save()
    else:
        pass

    survey_slug = referral_code.survey.slug
    page_slug = referral_code.survey.page_survey.all().order_by('slug')[0].slug

    return HttpResponseRedirect(reverse('skip_logic:page',
                                        kwargs={'survey_slug': survey_slug,
                                                'page_slug': page_slug,}))
