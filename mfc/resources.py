from import_export import resources
from .models import Branch, Service
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

class BranchResource(resources.ModelResource):
    def get_export_queryset(self):
        now = timezone.now()
        five_days_ago = now - timedelta(days=5)
        return Branch.objects.filter(
            created_at__gte=five_days_ago
        ).order_by('name')

    def dehydrate_is_active(self, branch):
        if branch.is_active:
            return "Активно"
        else:
            return "Неактивно"
    
    def get_address(self, branch):
        address = branch.address.strip()
        if len(address) > 15:
            return address[:15] + "..."
        return address

    class Meta:
        model = Branch
        fields = ('id','name','address','phone', 'email','work_schedule','is_active','created_at', 'updated_at')
        export_order = fields 

class ServiceResource(resources.ModelResource):
    def get_export_queryset(self):
        return Service.objects.filter(
            Q(category='DOC') | Q(category='TRANS') | Q(category='SOC')
        ).order_by('category', 'name')
    
    def dehydrate_category(self, service):
        category_names = {
            'DOC': 'Документы',
            'TRANS': 'Транспорт', 
            'SOC': 'Соц. услуги'
        }
        return category_names.get(service.category, service.get_category_display())
    
    def get_duration_assessment(self, service):
        if service.duration_days <= 3:
            return "Быстро (≤ 3 дней)"
        elif service.duration_days <= 7:
            return "Средне (4-7 дней)"
        else:
            return "Долго (> 7 дней)"
    
    class Meta:
        model = Service
        fields = ('id', 'name', 'category', 'duration_days', 'duration_assessment', 'created_at', 'updated_at')
        export_order = fields