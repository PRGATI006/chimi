"""
URL configuration for Fraud Detection Application
"""
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Authentication
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Certificate operations
    path('upload/', views.upload_certificate, name='upload'),
    path('result/<int:certificate_id>/', views.result_detail, name='result_detail'),
    path('download/pdf/<int:certificate_id>/', views.download_pdf_report, name='download_pdf'),
    path('download/json/<int:certificate_id>/', views.download_json_report, name='download_json'),
    path('delete/<int:certificate_id>/', views.delete_certificate, name='delete_certificate'),
    
    # History
    path('history/', views.certificate_history, name='history'),
]
