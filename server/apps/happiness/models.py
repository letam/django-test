from django.db import models
from django.conf import settings


class Happiness(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    level = models.PositiveSmallIntegerField()

    def __str__(self):
        return f'{self.date}\t{self.user.id}: {self.level}'
