from django.contrib import admin
from .models import Experiment, Parameter, Observation

admin.site.register(Experiment)
admin.site.register(Parameter)
admin.site.register(Observation)
