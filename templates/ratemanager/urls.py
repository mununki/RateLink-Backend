"""ratemanager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rate import views
# from graphene_django.views import GraphQLView
from graphene_file_upload.django import FileUploadGraphQLView
from django.views.decorators.csrf import csrf_exempt

# DEV !! MUST comment when deploy to real server
# from django.conf import settings
# from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(FileUploadGraphQLView.as_view(graphiql=True))),
    path('rates/search/', views.rateSearchedList, name='rateSearch'),
    path('rates/input/', views.rateInput, name='rateInput'),
    path('rates/duplicate/<int:pk>/', views.rateDuplicate, name='rateDuplicate'),
    path('rates/modify/<str:str>/<int:pk>/', views.rateModify, name='rateModify'),
    path('rates/delete/<str:str>/<int:pk>/', views.rateDelete, name='rateDelete'),
    path('rates/charts/', views.rateCharts, name='rateCharts'),
    path('account/', include('account.urls')),
    path('', views.main, name='main'),
    path('search/', include('countrycity.urls')),
    path('', include('api.urls')),
    # path('download/', views.rates_json, name='rateDownload'),

]

# DEV !! MUST comment when deploy to real server
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
