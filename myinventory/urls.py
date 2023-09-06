"""myinventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from stockmgmt import views
from custom_registration.views import CustomRegistrationView


urlpatterns = [
    path('', views.home, name='home'),
    path('list_items/', views.list_items, name='list_items'),
    path('list_history/', views.list_history, name='list_history'),
    path('item_detail/<str:pk>/', views.item_detail, name="item_detail"),
    path('issue_items/<str:pk>/', views.issue_items, name="issue_items"),
    path('receive_items/<str:pk>/', views.receive_items, name="receive_items"),
    path('reorder_level/<str:pk>/', views.reorder_level, name="reorder_level"),

    path('add_items/', views.add_items, name='add_items'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_location/', views.add_location, name='add_location'),
    path('add_room/', views.add_room, name='add_room'),

    path('update_items/<str:pk>/', views.update_items, name="update_items"),
    path('update_category/<str:pk>/',
         views.update_category, name="update_category"),
    path('update_location/<str:pk>/',
         views.update_location, name="update_location"),
    path('update_room/<str:pk>/',
         views.update_room, name="update_room"),

    path('delete_items/<str:pk>/', views.delete_items, name="delete_items"),
    path('delete_category/<str:pk>/',
         views.delete_category, name="delete_category"),
    path('delete_location/<str:pk>/',
         views.delete_location, name="delete_location"),
    path('delete_room/<str:pk>/',
         views.delete_room, name="delete_room"),

    path('admin/', admin.site.urls),

    path('accounts/register/', CustomRegistrationView.as_view(),
         name='registration_register'),
    # Other registration URLs
    path('accounts/', include('registration.backends.default.urls')),
]
