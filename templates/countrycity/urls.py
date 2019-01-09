from django.urls import path
from countrycity import views

urlpatterns = [
    path('location/', views.search_location, name='searchcity'),
    path('liner/', views.search_liner, name='searchliner'),
    path('locationcode/', views.find_location_code, name='find_location_code')
    # path('upload/location/', views.upload_location, name='upload_location'),
    # path('upload/rates/', views.upload_rates, name='upload_rates'),
    # path('upload/liner/', views.upload_liner, name='upload_liner'),
    # path('upload/client/', views.upload_client, name='upload_client'),
]
