from import_export import resources, fields
from .models import Branch, Service
from django.db.models import Q

class BranchResource(resources.ModelResource):
    phone_formatted = fields.Field(column_name='phone_formatted')
    
    class Meta:
        model = Branch
        fields = ('id', 'name', 'address', 'phone_formatted', 'email', 'work_schedule', 'is_active', 'created_at', 'updated_at')
        export_order = fields
    
    def get_export_queryset(self):
        return Branch.objects.filter(is_active=True).order_by('name')
    
    def dehydrate_address(self, branch):
        address = branch.address.strip()
        if len(address) > 15:
            return address[:15] + "..."
        return address
    
    def dehydrate_phone_formatted(self, branch):
        return self.get_phone_formatted(branch)
    
    def get_phone_formatted(self, branch):
        phone = branch.phone.strip()
        if phone.startswith('8') and len(phone) >= 11:
            return '+7' + phone[1:]
        elif phone.startswith('7') and len(phone) >= 11:
            return '+' + phone
        elif not phone.startswith('+') and len(phone) >= 10:
            return '+7' + phone
        else:
            return phone

class ServiceResource(resources.ModelResource):
    duration_assessment = fields.Field(column_name='duration_assessment')

    class Meta:
        model = Service
        fields = ('id', 'name', 'category', 'duration_days', 'duration_assessment', 'created_at', 'updated_at')
        export_order = fields

    def get_export_queryset(self):
        return Service.objects.filter(Q(category='DOC') | Q(category='TRANS') | Q(category='SOC')
        ).order_by('category', 'name')
    
    def dehydrate_category(self, service):
        category_names = {'DOC': 'Документы', 'TRANS': 'Транспорт',  'SOC': 'Соц. услуги'
        }
        return category_names.get(service.category, service.get_category_display())
    
    def dehydrate_duration_assessment(self, service):
        return self.get_duration_assessment(service)
    
    def get_duration_assessment(self, service):
        if service.duration_days <= 3:
            return "Быстро"
        elif service.duration_days <= 7:
            return "Средне"
        else:
            return "Долго"
