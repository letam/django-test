from django.db import models
from django.conf import settings


class Happiness(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    level = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = [['user', 'date']]


class Team(models.Model):
    name = models.CharField(max_length=150)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
