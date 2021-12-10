from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    MIN_LEVEL = 2

    user = models.OneToOneField(User, models.CASCADE)
    account_type = models.SmallIntegerField(default=0)

    is_complete = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    completion_level = models.SmallIntegerField(default=-1)
    verification_level = models.SmallIntegerField(default=-1)
    
    def __str__(self):
        return self.user.email
