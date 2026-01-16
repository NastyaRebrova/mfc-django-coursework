from django.urls import path, include
from . import views
from .api import BranchViewSet, ServiceViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'services', ServiceViewSet, basename='service')

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

    path('api/', include(router.urls)),
]

app_name = 'mfc'