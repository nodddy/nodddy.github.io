from django import forms
from .models import Parameter, Note, Step


class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = ('name', 'value', 'unit')


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('text',)

class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ('text', 'note')

