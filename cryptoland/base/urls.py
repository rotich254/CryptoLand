from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('logout/', views.logoutPage, name='logout'),

]
