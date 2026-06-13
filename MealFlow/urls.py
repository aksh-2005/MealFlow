"""
URL configuration for MealFlow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('edit_pass/', views.edit_pass, name='edit_pass'),
    path('edit_address/', views.edit_address, name='edit_address'),
    path('edit-meal-preference/', views.edit_meal_preference, name='edit_meal_preference'),
    path('review-meal/', views.review_meal, name='review_meal'),
    path('report-issue/', views.report_issue, name='report_issue'),
    path('plans/', views.plans, name='plans'),
    path('create-checkout-session/<str:plan_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('contact/', views.contact_us, name='contact_us'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]
