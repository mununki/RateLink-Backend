from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from countrycity.models import Location, Liner


class CNTRtype(models.Model):
    name = models.CharField(max_length=10, blank=False)

    class Meta:
        verbose_name = 'CNTR Type'
        verbose_name_plural = 'CNTR Types'

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=30, blank=False)
    salesman = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name='client')
    remarks = models.CharField(max_length=100, blank=True)
    recordedDate = models.DateField(default=timezone.now, blank=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.name


class Rate(models.Model):
    inputperson = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, blank=False, related_name='inputperson')
    account = models.ForeignKey(Client, on_delete=models.CASCADE, blank=False, related_name='rate')
    liner = models.ForeignKey(Liner, on_delete=models.CASCADE, blank=False, related_name='rate')
    pol = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, related_name='ratepol')
    pod = models.ForeignKey(Location, on_delete=models.CASCADE, blank=False, related_name='ratepod')
    type = models.ForeignKey(CNTRtype, on_delete=models.CASCADE, blank=False, related_name='rate')
    buying20 = models.IntegerField(default=0, blank=True)
    buying40 = models.IntegerField(default=0, blank=True)
    buying4H = models.IntegerField(default=0, blank=True)
    selling20 = models.IntegerField(default=0, blank=True)
    selling40 = models.IntegerField(default=0, blank=True)
    selling4H = models.IntegerField(default=0, blank=True)
    loadingFT = models.IntegerField(default=0, blank=True)
    dischargingFT = models.IntegerField(default=0, blank=True)
    offeredDate = models.DateField(default=timezone.now, blank=True)
    effectiveDate = models.DateField(default=timezone.now, blank=True)
    recordedDate = models.DateTimeField(auto_now=True)
    remark = models.TextField(max_length=100, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Rate'
        verbose_name_plural = 'Rates'
