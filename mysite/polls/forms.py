from django import forms
from .models import Experiment, Data


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('name', 'date')
        widgets = {'date': forms.SelectDateWidget(years=list(range(2015, 2022)))}
        labels = {'name': 'Experiment Name'}


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = Data
        fields=('name',)
