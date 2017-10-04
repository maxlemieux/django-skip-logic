"""
django-skip-logic forms.py
"""
from django.forms import ModelForm, Textarea, TextInput
from skip_logic.models import Campaign, Choice, Page, Path, Question, Reward, Survey

class CampaignModelForm(ModelForm):
    """Change form for Campaign model."""
    class Meta:
        model = Campaign
        fields = ['name', 'description', ]


class SurveyForm(ModelForm):
    """Change form for Survey model."""
    class Meta:
        model = Survey
        fields = ['title', 'pub_date', 'description', 'slug', 'call_to_action_label', 'call_to_action_url', 'call_to_action_text', ]
        widgets = {
            'title': TextInput(attrs={'size': 42,}),
            'description': Textarea(attrs={'cols': 40, 'rows': 5}),
            'call_to_action_label': TextInput(attrs={'size': 42,}),
            'call_to_action_url': TextInput(attrs={'size': 42,}),
            'call_to_action_text': Textarea(attrs={'cols': 40, 'rows': 5}),
        }


class PageForm(ModelForm):
    """Change form for Page model."""
    class Meta:
        model = Page
        fields = ['title', 'page_text', 'page_number', 'is_last', 'slug',]
        widgets = {
            'title': TextInput(attrs={'size': 42,}),
            'page_text': Textarea(attrs={'cols': 40, 'rows': 5}),
        }


class QuestionForm(ModelForm):
    """Change form for Question model."""
    class Meta:
        model = Question
        fields = ['question_text', 'question_number', 'layout_horizontal', 'required', 'slug',]
        widgets = {
            'question_text': Textarea(attrs={'cols': 40, 'rows': 5}),
        }


class ChoiceForm(ModelForm):
    """Change form for Choice model."""
    class Meta:
        model = Choice
        fields = ['choice_text', 'choice_number', 'choice_image', 'slug', 'input_field',]


class PathForm(ModelForm):
    """Change form for Path model."""
    class Meta:
        model = Path
        fields = ['page', 'slug',]


class RewardForm(ModelForm):
    """Change form for Reward model."""
    class Meta:
        model = Reward
        fields = ['name', 'description', 'image', 'in_store', 'point_cost', 'reward_level', ]
