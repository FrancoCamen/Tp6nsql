
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('airports/', views.airports, name='airports'),
    path('airports/popular', views.get_popular_airports, name='get_popular_airports'),
    path('airports/<str:iata_code>/', views.airport_by_iata, name='airport_by_iata'),
    path('airports/nearby', views.get_nearby_airports, name='get_nearby_airports'),
]
