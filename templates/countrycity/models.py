from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    label = models.CharField(max_length=10, blank=True)
    verbose_name_plural = 'Location'

    def __str__(self):
        return self.name

class Liner(models.Model):
    name = models.CharField(max_length=20)
    label = models.CharField(max_length=30)

    def __str__(self):
        return self.name
