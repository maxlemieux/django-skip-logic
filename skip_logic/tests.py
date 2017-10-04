import datetime
import random
import string
import unittest

from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User, Group, Permission

from skip_logic.models import Survey, Page, Question, Choice, Path, Campaign, UserProfile


class CreateSurveyViewTest(TestCase):
    fixtures = ['groups.json']

    def test_survey_creation_view_logged_out(self):
        c = Client()
        get_new_survey_response = c.get('/demo/surveys/new/')
        self.assertEqual(get_new_survey_response.status_code, 404)

        create_survey_response = c.post('/demo/surveys/new/', {'title': 'Test Survey', 'description': 'A test survey', 'slug': '1a2b3c4d', 'pub_date': timezone.now()})
        self.assertEqual(create_survey_response.status_code, 404)


class CreateSurveyTestCase(TestCase):
    """Integration test for survey component models as well as custom user profiles."""
    fixtures = ['groups.json']

    def new_slug(self):
        new_slug = ''.join(random.choice(string.ascii_uppercase +
                                         string.ascii_lowercase +
                                         string.digits) for _ in range(8))
        return new_slug

    def create_user(self, username=None, password=None, email=None):
        # https://stackoverflow.com/questions/19827342/django-test-client-does-not-log-in
        user_count = 0
        if username is None:
            username = "user%d" % user_count
            while User.objects.filter(username=username).count() != 0:
                user_count += 1
                username = "user%d" % user_count
        if password is None:
            password = "password"
        if email is None:
            email = "user%d@test.com" % user_count
        user_count += 1
        user = User.objects.create_user(username=username, password=password)
        group = Group.objects.get(name='Survey Creators')
        group.user_set.add(user)

        return user

    def create_survey(self, title=None, description=None, pub_date=None, author=None, slug=None):
        if title is None:
            title = "My New Survey"
        if description is None:
            description = "My New Survey description goes here."
        if pub_date is None:
            pub_date = timezone.now()
        if author is None:
            author = User.objects.get(username='test creator')
        if slug is None:
            slug = ''.join(random.choice(string.ascii_uppercase +
                                         string.ascii_lowercase +
                                         string.digits) for _ in range(8))

        survey = Survey.objects.create(title=title,
                                       description=description,
                                       pub_date=pub_date,
                                       author=author,
                                       slug=slug)
        return survey

    def create_page(self, survey=None, title=None, page_text=None, page_number=None, slug=None):
        if survey is None:
            raise ValueError("survey must be defined")
        if title is None:
            title = "My New Page"
        if page_text is None:
            description = "My New Page text goes here."
        if slug is None:
            slug = ''.join(random.choice(string.ascii_uppercase +
                                         string.ascii_lowercase +
                                         string.digits) for _ in range(8))
        if page_number is None:
            if Page.objects.filter(survey=survey).count() > 0:
                new_page_number = Page.objects.filter(survey=survey).\
                                               latest('page_number').page_number + 1
            else:
                new_page_number = 1

        page = Page.objects.create(survey=survey,
                                   title=title,
                                   page_text=page_text,
                                   page_number=new_page_number,
                                   slug=slug)
        return page

    def create_question(self, page=None, question_text=None, question_number=None, slug=None):
        if page is None:
            raise ValueError("page must be defined")
        if question_text is None:
            question_text = "My New Question text goes here."
        if slug is None:
            slug = ''.join(random.choice(string.ascii_uppercase +
                                         string.ascii_lowercase +
                                         string.digits) for _ in range(8))
        if question_number is None:
            if Question.objects.filter(page=page).count() > 0:
                new_question_number = Question.objects.filter(page=page).\
                                               latest('question_number').question_number + 1
            else:
                new_question_number = 1

        question = Question.objects.create(page=page, question_text=question_text, question_number=new_question_number, slug=slug)
        return question

    def create_choice(self, question=None, choice_text=None, choice_number=None, slug=None):
        if question is None:
            raise ValueError("question must be defined")
        if choice_text is None:
            choice_text = "My New Choice text goes here."
        if slug is None:
            slug = ''.join(random.choice(string.ascii_uppercase +
                                         string.ascii_lowercase +
                                         string.digits) for _ in range(8))
        if choice_number is None:
            if Choice.objects.filter(question=question).count() > 0:
                new_choice_number = Choice.objects.filter(question=question).\
                                               latest('choice_number').choice_number + 1
            else:
                new_choice_number = 1

        choice = Choice.objects.create(question=question, choice_text=choice_text, choice_number=new_choice_number, slug=slug)
        return choice

    def create_path(self,  choice=None, page=None, slug=None):
        if choice is None:
            raise ValueError("choice must be defined")
        if page is None:
            raise ValueError("choice must be defined")
        if slug is None:
            slug = ''.join(random.choice(string.ascii_uppercase +
                                         string.ascii_lowercase +
                                         string.digits) for _ in range(8))
        path = Path.objects.create(choice=choice, page=page, slug=slug)
        return path

    def test_create_user(self):
        user = self.create_user(username='test creator')

        self.assertTrue(isinstance(user, User))
        self.assertTrue(isinstance(user.userprofile, UserProfile))

    def test_survey_creation(self):
        user = self.create_user(username='test creator', password='password')
        survey_slug = self.new_slug()
        title = "Test Survey"

        survey = self.create_survey(author=user, title=title, slug=survey_slug)

        instance = Survey.objects.get(slug=survey_slug)
        self.assertTrue(isinstance(instance, Survey))
        self.assertEqual(instance.slug, survey_slug)

    def test_page_creation(self):
        user = self.create_user(username='test creator', password='password')
        survey_slug = self.new_slug()
        survey = self.create_survey(author=user, title='Test Survey', slug=survey_slug)
        page_slug = self.new_slug()
        page_text = "Example page text here"
        title = "Test Page 1"

        page = self.create_page(survey=survey, title=title, page_text=page_text, slug=page_slug)

        instance = Page.objects.get(slug=page_slug)
        self.assertTrue(isinstance(instance, Page))
        self.assertEqual(instance.page_text, page_text)
        self.assertEqual(instance.title, title)
        self.assertEqual(instance.slug, page_slug)

    def test_question_creation(self):
        user = self.create_user(username='test creator', password='password')
        survey_slug = self.new_slug()
        survey = self.create_survey(author=user, title='Test Survey', slug=survey_slug)
        page_slug = self.new_slug()
        page = self.create_page(survey=survey, title='Test Page 1', page_text='Example page text here', slug=page_slug)
        question_slug = self.new_slug()
        question_text = "Test Question P1Q1"

        question = self.create_question(page=page, question_text=question_text, slug=question_slug)

        instance = Question.objects.get(slug=question_slug)
        self.assertTrue(isinstance(instance, Question))
        self.assertEqual(instance.question_text, question_text)
        self.assertEqual(instance.slug, question_slug)
        self.assertEqual(instance.page, page)

    def test_choice_creation(self):
        user = self.create_user(username='test creator', password='password')
        survey_slug = self.new_slug()
        survey = self.create_survey(author=user, title='Test Survey', slug=survey_slug)
        page_slug = self.new_slug()
        page = self.create_page(survey=survey, title='Test Page 1', page_text='Example page text here', slug=page_slug)
        question_slug = self.new_slug()
        question = self.create_question(page=page, question_text="Test Question P1Q1", slug=question_slug)
        choice_slug = self.new_slug()
        choice_text = "Test Choice P1Q1C1"
        choice = self.create_choice(question=question, choice_text=choice_text, slug=choice_slug)

        instance = Choice.objects.get(slug=choice_slug)
        self.assertTrue(isinstance(instance, Choice))
        self.assertEqual(instance.choice_text, choice_text)
        self.assertEqual(instance.slug, choice_slug)
        self.assertEqual(instance.question, question)

    def test_path_creation(self):
        user = self.create_user(username='test creator', password='password')
        survey_slug = self.new_slug()
        survey = self.create_survey(author=user, title='Test Survey', slug=survey_slug)
        page1_slug = self.new_slug()
        page1 = self.create_page(survey=survey, title='Test Page 1', page_text='Example page text here', slug=page1_slug)
        page2_slug = self.new_slug()
        page2 = self.create_page(survey=survey, title='Test Page 2', page_text='Example page text here', slug=page2_slug)
        question1_slug = self.new_slug()
        question1 = self.create_question(page=page1, question_text="Test Question P1Q1", slug=question1_slug)
        question2_slug = self.new_slug()
        question2 = self.create_question(page=page2, question_text="Test Question P2Q1", slug=question2_slug)
        choice1_slug = self.new_slug()
        choice1 = self.create_choice(question=question1, choice_text="Test Choice P1Q1C1", slug=choice1_slug)
        choice2_slug = self.new_slug()
        choice2 = self.create_choice(question=question2, choice_text="Test Choice P2Q1C1", slug=choice2_slug)
        path_slug = self.new_slug()
        path = self.create_path(choice=choice1, page=page2, slug=path_slug)

        instance = Path.objects.get(slug=path_slug)
        self.assertTrue(isinstance(instance, Path))
        self.assertEqual(instance.choice, choice1)
        self.assertEqual(instance.page, page2)
