from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Branch, Service
from .serializers import BranchSerializer, ServiceSerializer

class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all().order_by('name')
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    permission_classes = [AllowAny]

    @action(detail=False, methods=['GET']) # получить только активные отделения
    def active(self, request):
        active_branches = Branch.objects.filter(Q(is_active=True)).order_by('name')
        page = self.paginate_queryset(active_branches)
        
        if page is not None:  # если пагинация включена
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(active_branches, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST']) #  переключить статус активности отделения
    def toggle_active(self, request, pk=None):
        branch = self.get_object()
        branch.is_active = not branch.is_active
        branch.save()
        serializer = self.get_serializer(branch)
        
        return Response({
            'message': f'Статус отделения изменен на {"активно" if branch.is_active else "неактивно"}',
            'branch': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET']) # сложный поиск с Q объектами
    def complex_search(self, request):
        query = request.query_params.get('query', '')
        active_only = request.query_params.get('active', 'false').lower() == 'true'
        q_objects = Q()
        
        if query:
            q_objects |= Q(name__icontains=query)
            q_objects |= Q(address__icontains=query)
        
        if active_only:
            q_objects &= Q(is_active=True)
        
        q_objects &= ~Q(email__icontains='test')
        
        branches = Branch.objects.filter(q_objects).order_by('name')
        
        page = self.paginate_queryset(branches)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(branches, many=True)
        return Response(serializer.data)
    
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('name')
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['GET']) # получение услуг с быстрым выполнением
    def fast_services(self, request):
        max_days = request.query_params.get('max_days')
        q_objects = Q()
        if max_days:
            try:
                max_days_int = int(max_days)
                q_objects &= Q(duration_days__lte=max_days_int)
            except ValueError: # если не число, то игнорируем
                pass

        or_condition = Q()
        or_condition |= Q(category='DOC') 
        or_condition |= Q(category='TRANS') 
        or_condition |= Q(duration_days__lte=3)
        
        q_objects &= or_condition
        
        q_objects &= ~Q(name__icontains='временная')
        
        services = Service.objects.filter(q_objects).order_by('name')
        
        page = self.paginate_queryset(services)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['POST']) # изменение срока выполнения услуги
    def update_duration(self, request, pk=None): 
        service = self.get_object()
        new_duration = request.data.get('duration_days')
    
        if not new_duration:
            return Response(
                {'error': 'Не указан новый срок выполнения'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_duration = int(new_duration)
            if new_duration < 1 or new_duration > 365:
                return Response(
                    {'error': 'Срок должен быть от 1 до 365 дней'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Срок должен быть числом'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service.duration_days = new_duration
        service.save()
        
        serializer = self.get_serializer(service)
        return Response({
            'message': f'Срок выполнения услуги изменен на {new_duration} дней',
            'service': serializer.data
        }, status=status.HTTP_200_OK)