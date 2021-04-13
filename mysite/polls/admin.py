from django.contrib import admin
from .models import Experiment, Parameter,  Note, Step, StepExperiment, StepParameter

admin.site.register(Experiment)
admin.site.register(Parameter)
admin.site.register(Note)
admin.site.register(Step)
admin.site.register(StepExperiment)
admin.site.register(StepParameter)
