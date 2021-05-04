from django.urls import path
from django import forms

from . import views
from . import models

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),

    path('experiment/<int:parent_id>/file_upload',
         views.ParameterUpdateView.as_view(),
         {'template_name': 'core/experiment-detail.html',
          'update_name': 'file',
          'model': models.File,
          'parent_model': models.Experiment,
          'fields': ['name', 'file', 'type', 'file_delimiter'],
          'formset_widgets': {'type': forms.Select(
              attrs={'id': 'filetype'}
          ),
              'file_delimiter': forms.Select(
                  attrs={'id': 'delimiter'}
              )},
          },
         name='file-upload'),

    path('experiment/<int:parent_id>/',
         views.ExperimentDetailView.as_view(),
         name='experiment-detail'),

    path('experiment/<int:parent_id>/<int:file_id>/<str:file_type>/',
         views.FileView.as_view(),
         name='file-viewer'),

    path('create_experiment',
         views.ExperimentUpdateView.as_view(),
         {'template_name': 'core/index.html',
          'parent_model': models.Experiment},
         name='create-experiment'),

    path('experiment/<int:parent_id>/update_experiment',
         views.ExperimentUpdateView.as_view(),
         {'template_name': 'core/experiment-detail.html',
          'update_name': 'experiment',
          'parent_model': models.Experiment
          },
         name='update-experiment'),

    path('experiment/<int:parent_id>/update_parameter',
         views.ParameterUpdateView.as_view(),
         {'template_name': 'core/experiment-detail.html',
          'model': models.Parameter,
          'parent_model': models.Experiment,
          'fields': ['name', 'value', 'unit'],
          'update_name': 'parameter'
          },
         name='experiment-update-parameter'),

    path('experiment/<int:parent_id>/update_step',
         views.ChildUpdateView.as_view(),
         {'template_name': 'core/step-update.html',
          'model': models.Step,
          'parent_model': models.Experiment,
          'child_model': models.Parameter,
          'child_fields': ['name', 'value', 'unit'],
          'fields': ['text'],
          'formset_widgets': {'text': forms.Textarea(attrs={"rows": 1}),
                              'note': forms.Textarea(attrs={"rows": 1})}
          },
         name='experiment-update-step'),

    path('experiment/<int:parent_id>/update_note',
         views.ParameterUpdateView.as_view(),
         {'template_name': 'core/experiment-detail.html',
          'model': models.Note,
          'parent_model': models.Experiment,
          'fields': ['text'],
          'formset_widgets': {'text': forms.Textarea(attrs={"rows": 3})},
          'update_name': 'note'
          },
         name='experiment-update-note'),

    path('sample/<int:parent_id>/', views.SampleDetailView.as_view(),
         name='sample-detail'),

    path('sample/<int:parent_id>/update_parameter',
         views.ParameterUpdateView.as_view(),
         {'template_name': 'core/sample-detail.html',
          'model': models.Parameter,
          'parent_model': models.Sample,
          'fields': ['name', 'value', 'unit'],
          'update_name': 'parameter'
          },
         name='sample-update-parameter'),

    path('sample/<int:parent_id>/update_note',
         views.ParameterUpdateView.as_view(),
         {'template_name': 'core/sample-detail.html',
          'model': models.Note,
          'parent_model': models.Sample,
          'fields': ['text'],
          'formset_widgets': {'text': forms.Textarea(attrs={"rows": 3})},
          'update_name': 'note'
          },
         name='sample-update-note'),

]
