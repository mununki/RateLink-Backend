from django.urls import path, re_path
from account import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.SignupRateManager, name='signup'),
    path('login/', views.LoginRateManager, name='login'),
    path('logout/', views.LogoutRateManager, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/', views.ProfileUpdate, name='profileupdate'),
    path('friend/', views.ReaderUpdate, name='readerupdate'),
    path('friend/add/<pk>', views.ReaderAdd, name='readeradd'),
    path('friend/delete/<pk>', views.ReaderDelete, name='readerdelete'),
    path('changepassword/', views.ChangePassword, name='changepassword'),
    path('findid/', views.FindID, name='findid'),
    path('password_reset/', auth_views.password_reset, name='password_reset'),
    path('password_reset/done/', auth_views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', auth_views.password_reset_complete, name='password_reset_complete'),
    path('signup/ajax/validate_email/', views.validate_email, name='validate_email'),
    # path('message/', views.MessageList, name='messageList'),
]
