from django.contrib import admin
from .models import Experiment, Parameter,  Note, Step, Sample, File

admin.site.register(Experiment)
admin.site.register(Parameter)
admin.site.register(Note)
admin.site.register(Step)
admin.site.register(Sample)
admin.site.register(File)

