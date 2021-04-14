from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:experiment_id>/', views.detail, name='detail'),
    path('<int:experiment_id>/<form_id>/add', views.add, name='add'),
    path('<int:experiment_id>/<str:model_id><entry_id>/delete', views.delete, name='delete'),
    path('add', views.add_experiment, name='add_experiment'),
]
