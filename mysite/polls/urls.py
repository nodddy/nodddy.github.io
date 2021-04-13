from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    # ex: /polls/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /polls/5/
    path('<int:experiment_id>/', views.detail, name='detail'),
    path('<int:experiment_id>/<form_id>/add', views.add, name='add'),
    path('<int:experiment_id>/<form_id>/delete', views.delete, name='delete'),
]
