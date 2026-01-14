from django.urls import path
from . import views

app_name = 'mfc'

urlpatterns = [
    # список всех отделений
    path('', views.branch_list, name='branch_list'),
    
    # детальная информация об отделении
    path('branches/<int:pk>/', views.branch_detail, name='branch_detail'),
    
    # создание нового отделения
    path('branches/create/', views.branch_create, name='branch_create'),
    
    # редактирование отделения
    path('branches/<int:pk>/edit/', views.branch_edit, name='branch_edit'),
    
    # удаление отделения
    path('branches/<int:pk>/delete/', views.branch_delete, name='branch_delete'),
]