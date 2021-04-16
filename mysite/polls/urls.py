from django.urls import path

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
         views.ParameterUpdateView.as_view(template_name='polls/parameter-update.html',
                                           parent_model=models.Sample,
                                           fields=['name', 'value', 'unit']
                                           ),
         name='sample-update-parameter'),

]
