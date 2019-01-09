from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from api import views
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('signup', views.UserCreateViewSet)
router.register('userupdate', views.UserUpdateViewSet)
router.register('ratereader', views.RateReaderViewSet, base_name='ratereader')
router.register('rates', views.RateViewSet, base_name='rateswithtellers')
router.register('ratesip', views.RateInputpersonViewSet, base_name='ratesbyinputperson')
router.register('ratesac', views.RateAccountViewSet, base_name='ratesbyaccount')
router.register('ratesln', views.RateLinerViewSet, base_name='ratesbyliner')
router.register('ratespl', views.RatePolViewSet, base_name='ratesbypol')
router.register('ratespd', views.RatePodViewSet, base_name='ratesbypod')
router.register('liners', views.LinerViewSet, base_name='linerlist')
router.register('locations', views.LocationViewSet, base_name='locationlist')

# from .views import MyObtainAuthToken

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/changepw/', views.UpdatePassword.as_view(), name='updatepassword'),
    path('api/changeprofileimage/', views.UpdateProfileImage.as_view(), name='updateprofileimage'),
    path('api/rateschart/', views.RateChartView.as_view(), name='rateschart'),
    path('api/usersearch/', views.UserSearchView.as_view(), name='usersearch'),
    path('api/ratereaderuser/', views.RateReaderUserView.as_view(), name='ratereaderuser'),
    path('api/rateshoweruser/', views.RateShowerUserView.as_view(), name='rateshoweruser'),
    path('api/ratesheader/', views.RateHeaderView.as_view(), name='ratesheader'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
]