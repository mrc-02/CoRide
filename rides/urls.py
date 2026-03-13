from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_rides, name='list-rides'),
    path('create/', views.create_ride, name='create-ride'),
    path('<int:rid>/', views.ride_detail, name='ride-detail'),
]
