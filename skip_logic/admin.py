from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
#from django.db import models
#from django.forms import TextInput, Textarea

from .models import Survey, Page, Question, Choice, Path, QuestionResult
from .models import UserProfile, AvatarItem, AvatarStorage, Reward, RewardLevel
from .models import Campaign, ReferralCode

# Crashes if Display Name etc are set inline on new user creation.
# May need to be populated during new User save triggered creation.
#
#class UserProfileInline(admin.StackedInline):
#    """Admin for User Profile Inline model."""
#    model = UserProfile
#    can_delete = False
#    verbose_name_plural = "User Profiles"

class UserAdmin(BaseUserAdmin):
    """Admin for User model."""
#    inlines = (UserProfileInline, )


class AvatarItemAdmin(admin.ModelAdmin):
    """Admin for Avatar Item model."""
    model = AvatarItem


class AvatarStorageAdmin(admin.ModelAdmin):
    """Admin for Avatar Storage model."""
    model = AvatarStorage


class RewardAdmin(admin.ModelAdmin):
    """Admin for Reward model."""
    model = Reward
    list_display = ('id', 'name', 'description', 'image', 'point_cost')


class RewardLevelAdmin(admin.ModelAdmin):
    """Admin for Reward model."""
    model = RewardLevel
    list_display = ('id', 'name', 'description')


class UserProfileAdmin(admin.ModelAdmin):
    """Admin for User Profile model."""
    model = UserProfile


class PathAdmin(admin.ModelAdmin):
    def page__survey(self, obj):
        return obj.page.survey.title

    page__survey.short_description = "Survey"

    def choice__page_number(self, obj):
        try:
            choice = obj.choice
            return obj.choice.question.page.page_number
        except:
            return obj.origin_page.page_number

    choice__page_number.short_description = "Origin Page"

    def page__page_number(self, obj):
        return obj.page.page_number

    page__page_number.short_description = "Destination Page Number"
    model = Path
    list_display = ('id', 'slug', 'origin_page', 'choice', 'choice__page_number', 'page', 'page__page_number', 'page__survey')
    ordering = ('page__survey', 'page__page_number', )
    list_filter = ('page__survey', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(page__survey__author=request.user)


class PageInline(admin.TabularInline):
    """Admin for Page Inline model."""
    model = Page
    show_change_link = True


class QuestionInline(admin.TabularInline):
    """Admin for Question Inline model."""
    model = Question
    show_change_link = True
#    ordering = ('question_number',)


class PageAdmin(admin.ModelAdmin):
    """Admin for Page model."""
    inlines = [
        QuestionInline,
    ]
    list_display = ('id', 'slug', 'title', 'page_text', 'page_number', 'survey', )
    list_display_links = ('id', 'page_text', )
    list_filter = ('survey', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(survey__author=request.user)



class SurveyAdmin(admin.ModelAdmin):
    """Admin for Survey model."""
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def page__count(self, obj):
        return Page.objects.filter(survey__id=obj.id).count()
    page__count.short_description = "Pages"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    inlines = [
        PageInline,
    ]
    list_display = ('id', 'slug', 'title', 'page__count', 'call_to_action_label', 'call_to_action_url')
    list_display_links = ('id', 'title', )
#    formfield_overrides = {
#        models.CharField: {'widget': TextInput(attrs={'size':20})}
#    }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)



class ChoiceInline(admin.TabularInline):
    """Admin for Choice Inline model."""
    model = Choice
    show_change_link = True


class QuestionAdmin(admin.ModelAdmin):
    """Admin for Question model."""
    def choice__count(self, obj):
        return Choice.objects.filter(question__id=obj.id).count()
    choice__count.short_description = "Choices"

    def page__survey(self, obj):
        return obj.page.survey.title
    page__survey.short_description = "Survey"

    model = Question
    list_display = ('id', 'slug', 'question_text', 'question_number', 'choice__count', 'required', 'page__survey')
    list_display_links = ('id', 'question_text', 'question_number')
    inlines = [
        ChoiceInline,
    ]
    list_filter = ('page__survey', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(page__survey__author=request.user)



class ChoiceAdmin(admin.ModelAdmin):
    """Admin for Choice model."""
    def question__page__survey(self, obj):
        """Get the label for the survey associated with this choice."""
        return obj.question.page.survey.title
    question__page__survey.short_description = "Survey"

    def question__page(self, obj):
        """Get the label for the page associated with this choice."""
        return obj.question.page.page_text
    question__page.short_description = "Page"

    list_display = ('id', 'slug', 'choice_text', 'choice_number', 'votes', 'question', 'choice_image', 'question__page', 'question__page__survey')
    list_display_links = ('id', 'choice_text', 'choice_number')
    list_filter = ('question__page__survey',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(question__page__survey__author=request.user)


class QuestionResultAdmin(admin.ModelAdmin):
    """Admin for QuestionResult model."""
    model = QuestionResult

    def questionresult__survey(self, obj):
        """Get the Survey associated with this question result."""
        return obj.question.page.survey.title
    questionresult__survey.short_description = "Survey"

    fields = ('question', 'session', 'user', 'user_ip_address', 'result_object', 'input_text', 'result_date',)
    list_display = ('question', 'questionresult__survey', 'user', 'user_ip_address', 'result_object', 'input_text', 'result_date',)
#    list_filter = ("question")
    list_filter = ('question__page__survey', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(question__page__survey__author=request.user)


class CampaignAdmin(admin.ModelAdmin):
    """Admin for Campaign model."""
    model = Campaign

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)



class ReferralCodeAdmin(admin.ModelAdmin):
    """Admin for ReferralCode model."""
    model = ReferralCode
    list_display = ('code', 'campaign', 'survey', 'created_date', 'last_used_date', 'last_ip')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(survey__author=request.user)



admin.site.register(AvatarItem, AvatarItemAdmin)
admin.site.register(AvatarStorage, AvatarStorageAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Path, PathAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionResult, QuestionResultAdmin)
admin.site.register(ReferralCode, ReferralCodeAdmin)
admin.site.register(Reward, RewardAdmin)
admin.site.register(RewardLevel, RewardLevelAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
