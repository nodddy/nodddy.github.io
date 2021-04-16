from django import forms
from .models import Experiment, Parameter, Note, Step, Sample
from django.forms.models import inlineformset_factory


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ('name',)

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
        fields = ['text']


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['text', 'note']


ParameterFormSet = inlineformset_factory(Experiment, Parameter, fields=('name', 'value', 'unit'), extra=1, can_delete=True)
StepFormSet = inlineformset_factory(Experiment, Step, fields=('text', 'note'), extra=1)
NoteFormSet = inlineformset_factory(Experiment, Note, fields=('text',), extra=1)
