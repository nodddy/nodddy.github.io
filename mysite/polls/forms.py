from django import forms
from .models import Experiment, Parameter, Note, Step


class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = ('name', 'value', 'unit')


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('name', 'date', 'sample')
        widgets = {'date': forms.SelectDateWidget(years=list(range(2015, 2022)))}
        labels = {'name': 'Experiment Name'}


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('text',)


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ('text', 'note')
