"""
Models.py for django-skip-logic.
"""
import datetime
from math import floor

from ipware.ip import get_ip

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Campaign(models.Model):
    """Survey campaigns. Used to organize access to referral codes."""
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000, blank=True, null=True)
    created_date = models.DateTimeField('date created', default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ReferralCode(models.Model):
    """Referral Codes, handed out via email and parsed from url parameters on first visit."""
    # The code is 32 characters long
    code = models.CharField(max_length=32)
    # Each Referral Code points to a Survey
    survey = models.ForeignKey(
        'Survey',
        on_delete=models.CASCADE,
        related_name='referralcode_survey',
    )
    # We need this reference even though Survey has a ManyToMany field to Campaign,
    # because a referral code can only belong to one campaign.
    campaign = models.ForeignKey(
        'Campaign',
        on_delete=models.CASCADE,
        related_name='referralcode_campaign',
    )
    created_date = models.DateTimeField('date created', default=timezone.now)
    last_used_date = models.DateTimeField('date last used', blank=True, null=True)

    # Magic number 46!
    # https://stackoverflow.com/questions/166132/maximum-length-of-the-textual-representation-of-an-ipv6-address
    last_ip = models.CharField('last ip address used', max_length=46, blank=True, null=True)

    geoip_city = models.CharField(max_length=50, blank=True, null=True)
    geoip_state = models.CharField(max_length=50, blank=True, null=True)
    geoip_postal_code = models.CharField(max_length=50, blank=True, null=True)
    geoip_country = models.CharField(max_length=50, blank=True, null=True)

    def update_last_used_date(self):
        self.last_used_date = timezone.now()
        self.save()


# Override 'User' save method, to auto create User Profile
def create_profile(sender, **kwargs):
    """Create a user profile at user registration time."""
    # Pylint complains about sender unless the following comment is present:
    # pylint: disable=W0612,W0613
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = UserProfile(user=user)
        user_profile.save()
post_save.connect(create_profile, sender=User)


# this might all be unnecessary if Rewards can be used
# with more clearly named bridge table
class AvatarStorage(models.Model):
    """Attempt to implement an inventory space, or trophy case for users."""
    stored_item = models.ForeignKey(
        'AvatarItem',
        on_delete=models.CASCADE,
        related_name='avatarstorage_avataritem',
    )
    userprofile = models.ForeignKey(
        'UserProfile',
        on_delete=models.CASCADE,
        related_name='avatarstorage_userprofile',
    )
    stored_avataritem_quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.stored_reward.reward_text


# this might all be unnecessary if Rewards can be used
class AvatarItem(models.Model):
    """Things to go in AvatarStorage, like trophies or badges."""
    item_text = models.CharField(max_length=200)
    item_image = models.ImageField(blank=True)
    item_image_css_id = models.CharField(max_length=200)

    def __str__(self):
        return self.item_text


class RewardLevel(models.Model):
    """Reward levels."""
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Reward(models.Model):
    """Rewards to spend Points on."""
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    image = models.ImageField(blank=True, null=True)
    in_store = models.BooleanField(default=False)
    point_cost = models.PositiveIntegerField(default=0)
    reward_level = models.ForeignKey(
        'RewardLevel',
        on_delete=models.SET_NULL,
        blank=True, null=True
    )

    def price_gold(self):
        """Show me just the gold"""
        price_gold = floor(self.reward_cost / 100)
        return price_gold

    def price_silver(self):
        """Show me just the silver"""
        gold = self.price_gold()
        price_silver = floor(self.reward_cost / 10) - (gold * 10)
        return price_silver

    def price_copper(self):
        """Show me just the copper"""
        gold = self.price_gold()
        silver = self.price_silver()
        price_copper = self.reward_cost - (gold * 100 + silver * 10)
        return price_copper

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Fancy information about a User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_display_name = models.CharField(max_length=30, blank=True)
    user_avatar = models.ImageField(blank=True)
    user_profile_private = models.BooleanField(default=False)
    user_email = models.CharField(max_length=200, blank=True)
    user_zipcode = models.CharField(max_length=20, blank=True)
    user_email_opt_in = models.BooleanField(
        default=True,
        verbose_name="Yes, please send me occasional special offers from our partners."
    )
    user_currency = models.PositiveIntegerField(default=0, blank=True)
    user_experience = models.PositiveIntegerField(default=0, blank=True)
    user_registration_date = models.DateTimeField('date registered', default=timezone.now)

    def currency_gold(self):
        """Show me just the gold."""
        currency_gold = floor(self.user_currency / 100)
        return currency_gold

    def currency_silver(self):
        """Show me just the silver."""
        gold = self.currency_gold()
        currency_silver = floor(self.user_currency / 10) - (gold * 10)
        return currency_silver

    def currency_copper(self):
        """Show me just the copper."""
        gold = self.currency_gold()
        silver = self.currency_silver()
        currency_copper = self.user_currency - (gold * 100 + silver * 10)
        return currency_copper

    def receive_currency(self, currency_amount):
        """Give this user currency."""
        self.user_currency += currency_amount
        self.save()

    def receive_experience(self, experience_amount):
        """Give this user XP."""
        self.user_experience += experience_amount
        self.save()

    def __str__(self):
        return self.user_display_name


class Survey(models.Model):
    """Main survey object."""
    slug = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', blank=True, null=True)
    is_public = models.BooleanField(default=False)
    description = models.CharField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='survey_author')
    call_to_action_label = models.CharField(max_length=100, default='', blank=True, null=True)
    call_to_action_url = models.CharField(max_length=200, default='', blank=True, null=True)
    call_to_action_text = models.CharField(max_length=5000, default='', blank=True, null=True)
    campaign = models.ManyToManyField(Campaign, blank=True)

    # Use survey_length for branching surveys,
    # For roughly calculating progress based on the number of pages completed.
    survey_length = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        verbose_name = "    Survey"
        verbose_name_plural = "    Surveys"

    def was_published_recently(self):
        """Checks if this survey was published in the last day."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def __str__(self):
        return self.title


class Page(models.Model):
    """Displays a question."""
    slug = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    page_text = models.CharField(max_length=2000, blank=True, null=True)
    survey = models.ForeignKey(
        'Survey',
        on_delete=models.CASCADE,
        related_name='page_survey',
        blank=True, null=True,
    )

    page_number = models.IntegerField(
        default=1,
    )

    is_last = models.BooleanField(default=False)

    class Meta:
        ordering = ['page_number']
        # Dark pattern in all models' "verbose_name" values:
        # Initial spaces are stripped before they appear in the UI, but they affect the sort order.
        verbose_name = "   Page"
        verbose_name_plural = "   Pages"
        unique_together = ('page_number', 'survey', )

#    def save(self, *args, **kwargs):
#        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Choice(models.Model):
    """
    Defines possible answers to Questions, as text and/or images.
    """
    # For choice_text, allow null for questions with just an input field for the answer.
    slug = models.CharField(max_length=50)
    choice_text = models.CharField(max_length=200, blank=True, null=True)
    choice_number = models.IntegerField(default=1)
    votes = models.IntegerField(default=0)
    choice_image = models.ImageField(upload_to='choice_images/', blank=True, null=True)
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='choice_question',
        blank=True, null=True,
#        unique_together = ('choice_number', 'question', )
    )
    input_field = models.BooleanField(default=False)

    class Meta:
        ordering = ['choice_number', 'question']
        verbose_name = " Choice"
        verbose_name_plural = " Choices"

    def __str__(self):
        if self.input_field == True:
            return str(str(self.question.question_text) + " - Input Field")
        else:
            return str(str(self.question.question_text) + " - " + str(self.choice_text))


class Question(models.Model):
    """
    Displays text and choices.
    """
    slug = models.CharField(max_length=50)
    question_text = models.CharField(max_length=200, blank=True)
    question_number = models.IntegerField()
    layout_horizontal = models.BooleanField(default=False)
    required = models.BooleanField(default=False)
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='question_page',
        blank=True, null=True,
    )

    class Meta:
        ordering = ['question_number']
        verbose_name = "  Question"
        verbose_name_plural = "  Questions"
        unique_together = ('question_number', 'page', )

    def __str__(self):
        return self.question_text


class Path(models.Model):
    """
    Branch logic connecting a choice to a page.
    """
    slug = models.CharField(max_length=50)
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='path_choice'
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='path_page'
    )

    class Meta:
        verbose_name = "Path"
        verbose_name_plural = "Paths"

    def __str__(self):
        return self.page.title


class QuestionResult(models.Model):
    """
    An individual answer to a question.
    """
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='questionresult_question'
    )
    session = models.CharField(max_length=40)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questionresult_user',
        null=True,
        blank=True,
    )
    username = models.CharField(max_length=50, blank=True, null=True)
    user_ip_address = models.CharField(max_length=50, blank=True, null=True)
    result = models.CharField(max_length=1024, blank=True, null=True)
    result_object = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='questionresult_choice'
    )

    input_text = models.CharField(max_length=1024, blank=True, null=True)
    result_date = models.DateTimeField('date surveyed', default=timezone.now)

    class Meta:
        verbose_name = "     QuestionResult"
        verbose_name_plural = "     QuestionResults"

    def __str__(self):
        return str(self.question.question_text)
