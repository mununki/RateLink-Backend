from django.urls import path
from countrycity import views

urlpatterns = [
    path('location/', views.search_location, name='searchcity'),
    path('liner/', views.search_liner, name='searchliner'),
    path('locationcode/', views.find_location_code, name='find_location_code'),
]
