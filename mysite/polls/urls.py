from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:experiment_id>/', views.detail, name='detail'),
    path('<int:experiment_id>/<str:model_id><int:entry_id>/delete', views.delete, name='delete'),
    path('add', views.ExperimentCreateView.as_view(), name='add_experiment'),
    path('<int:experiment_id>/update', views.ExperimentUpdateView.as_view(), name='update_experiment'),
    path('<int:experiment_id>/update_parameter', views.ParameterUpdateView.as_view(), name='update_parameter'),

]
