from django.urls import path
from django import forms

from . import views
from . import models

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),

    path('experiment/<int:parent_id>/', views.ExperimentDetailView.as_view(),
         name='experiment-detail'),
    path('experiment/<int:parent_id>/update_note', views.ExperimentUpdateView.as_view(),
         name='experiment-update-note'),
    path('experiment/<int:parent_id>/update_step', views.ExperimentUpdateView.as_view(),
         name='experiment-update-step'),
    path('experiment/<int:parent_id>/update_parameter', views.ExperimentUpdateView.as_view(),
         name='experiment-update-parameter'),
    path('sample/<int:parent_id>/', views.SampleDetailView.as_view(),
         name='sample-detail'),
    path('sample/<int:parent_id>/update_parameter',
         views.ParameterUpdateView.as_view(),
         {'template_name': 'polls/parameter-update.html',
          'model': models.Parameter,
          'parent_model': models.Sample,
          'fields': ['name', 'value', 'unit']
          },
         name='sample-update-parameter'),
    path('experiment/<int:parent_id>/update_step',
         views.ParameterUpdateView.as_view(),
         {'template_name': 'polls/parameter-update.html',
          'model': models.Parameter,
          'parent_model': models.Sample,
          'fields': ['name', 'value', 'unit']
          },
         name='experiment-update-step'),
    path('sample/<int:parent_id>/update_note',
         views.ParameterUpdateView.as_view(),
         {'template_name': 'polls/note-update.html',
          'model': models.Note,
          'parent_model': models.Sample,
          'fields': ['text'],
          'formset_widgets': {'text': forms.Textarea}
          },
         name='sample-update-note'),

]
