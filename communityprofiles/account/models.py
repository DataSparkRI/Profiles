from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    is_general_public = models.BooleanField(default=False)
    is_community_advocate = models.BooleanField(default=False)
    is_journalist = models.BooleanField(default=False)
    is_researcher = models.BooleanField(default=False)
    is_grant_writer = models.BooleanField(default=False)
    is_city_state_agency_staff = models.BooleanField(default=False)
    is_consultant = models.BooleanField(default=False)
    is_legislator = models.BooleanField(default=False)
    is_policy_analyst = models.BooleanField(default=False)
    is_other = models.BooleanField(default=False)
    organization = models.CharField(max_length=300,default='',blank=True)
    org_is_non_profit = models.BooleanField(default=False)
    org_is_state_city_agency = models.BooleanField(default=False)
    org_is_university = models.BooleanField(default=False)
    org_is_other = models.BooleanField(default=False)
    wants_notifications = models.BooleanField(default=False)

@receiver(post_save)
def create_profile(sender, instance, created, **kwargs):
    if sender is User and created:
        UserProfile.objects.get_or_create(user=instance)
