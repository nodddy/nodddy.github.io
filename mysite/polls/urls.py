from django.urls import path

from . import views

app_name='polls'
urlpatterns = [
    # ex: /polls/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /polls/5/
    path('<int:experiment_id>/', views.detail, name='detail'),
    path('<int:experiment_id>/add_parameter', views.add_parameter, name='add_parameter'),
    path('<int:experiment_id>/add_step', views.add_data_to_model, name='add_data_to_model'),
    path('<int:experiment_id>/add_note', views.add_data_to_model, name='add_data_to_model')
]
