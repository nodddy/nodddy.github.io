from django.urls import path

from . import views

app_name='polls'
urlpatterns = [
    # ex: /polls/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /polls/5/
    path('<int:experiment_id>/', views.detail, name='detail'),
]
