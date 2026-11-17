from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('create/', views.create_request, name='create_request'),
    path('api/telemetry/', views.api_telemetry, name='api_telemetry'),
    path('<int:pk>/', views.request_detail, name='request_detail'),
    path('<int:pk>/change-status/<str:new_status>/', views.change_status, name='change_status'),
    path('<int:pk>/add-comment/', views.add_comment, name='add_comment'),
]