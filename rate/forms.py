from django import forms
from .models import Rate
from account.models import MyUser


class PostRateForm(forms.ModelForm):

    class Meta:
        model = Rate
        fields = ('account',
                  'liner',
                  'pol',
                  'pod',
                  'buying20',
                  'selling20',
                  'buying40',
                  'selling40',
                  'buying4H',
                  'selling4H',
                  'loadingFT',
                  'dischargingFT',
                  'offeredDate',
                  'effectiveDate',
                  'remark',
                  'deleted',
                  )

class PostSearchForm(forms.ModelForm):

    inputperson = forms.ModelChoiceField(queryset = MyUser.objects.all())

    class Meta:
        model = Rate
        fields = ('account',
                  'liner',
                  'pol',
                  'pod',
                  )
