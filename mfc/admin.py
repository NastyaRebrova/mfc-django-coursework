from django.contrib import admin
from django.utils import timezone
from django.utils.timesince import timesince
from import_export.admin import ExportMixin 
from .resources import BranchResource, ServiceResource 
from simple_history.admin import SimpleHistoryAdmin
from import_export.formats.base_formats import XLSX, CSV

from .models import Branch, Service, BranchService, UserProfile, Employee, Appointment

class BranchServiceInline(admin.TabularInline):
    model = BranchService
    extra = 1  # сколько пустых форм показываем
    show_change_link = True 
    fields = ['service', 'is_available', 'updated_at']
    readonly_fields = ['updated_at']
    
class ServiceBranchInline(admin.TabularInline):
    model = BranchService
    extra = 1
    show_change_link = True
    fields = ['branch', 'is_available', 'updated_at']
    readonly_fields = ['updated_at']

class BranchAdmin(ExportMixin, SimpleHistoryAdmin):
    resource_class = BranchResource 
    export_formats = [XLSX, CSV]
    list_display = ['id', 'name', 'phone', 'is_active', 'created_at', 'time_since_update']
    list_filter = ['is_active', 'updated_at']
    search_fields = ['name', 'address', 'phone', 'email']
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'address', 'phone', 'email', 'photo']
        }),
        ('Расписание и статус', {
            'fields': ['work_schedule', 'is_active']
        }),
        ('Даты', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']  # сворачиваемый блок
        }),
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [BranchServiceInline]
    @admin.display(description='Обновлено')
    def time_since_update(self, obj):
        if obj.updated_at:
            time_diff = timesince(obj.updated_at, timezone.now())
            return f"{time_diff} назад"
        return "—"
    list_display_links = ['id', 'name']
    ordering = ['-updated_at']

    def get_export_queryset(self, request):
        return self.resource_class().get_export_queryset()

class ServiceAdmin(ExportMixin, SimpleHistoryAdmin):
    resource_class = ServiceResource 
    export_formats = [XLSX, CSV]
    list_display = ['id', 'name', 'category', 'duration_days', 'created_at', 'time_since_update']
    list_filter = ['category', 'updated_at']
    search_fields = ['name']
    fieldsets = [
        ('Основная информация', {
            'fields': ['name', 'category', 'duration_days']
        }),
        ('Даты', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ServiceBranchInline]
    @admin.display(description='Обновлено')
    def time_since_update(self, obj):
        if obj.updated_at:
            time_diff = timesince(obj.updated_at, timezone.now())
            return f"{time_diff} назад"
        return "—"
    list_display_links = ['id', 'name']
    ordering = ['name']

    def get_export_queryset(self, request):
        return self.resource_class().get_export_queryset()

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'email', 'role', 'created_at', 'time_since_update']
    list_filter = ['role', 'updated_at']
    search_fields = ['full_name', 'email', 'phone', 'user__username']
    fieldsets = [
        ('Пользователь', {
            'fields': ['user', 'role']
        }),
        ('Контактная информация', {
            'fields': ['full_name', 'email', 'phone']
        }),
        ('Даты', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    readonly_fields = ['created_at', 'updated_at']
    @admin.display(description='Обновлено')
    def time_since_update(self, obj):
        if obj.updated_at:
            time_diff = timesince(obj.updated_at, timezone.now())
            return f"{time_diff} назад"
        return "—"
    list_display_links = ['id', 'user', 'full_name']
    ordering = ['full_name']

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_profile', 'office', 'position', 'created_at', 'time_since_update']
    list_filter = ['position', 'office', 'updated_at']
    search_fields = ['user_profile__full_name']
    fieldsets = [
        ('Сотрудник', {
            'fields': ['user_profile', 'position']
        }),
        ('Рабочее место', {
            'fields': ['office']
        }),
        ('Даты', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    readonly_fields = ['created_at', 'updated_at']
    @admin.display(description='Обновлено')
    def time_since_update(self, obj):
        if obj.updated_at:
            time_diff = timesince(obj.updated_at, timezone.now())
            return f"{time_diff} назад"
        return "—"
    list_display_links = ['id', 'user_profile']
    ordering = ['updated_at']

class AppointmentAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'user_profile', 'service', 'branch', 'date', 'time', 'status', 'created_at', 'time_since_update']
    list_filter = ['status', 'branch', 'service', 'updated_at']
    search_fields = ['user_profile__full_name', 'date']
    fieldsets = [
        ('Клиент и услуга', {
            'fields': ['user_profile', 'service', 'branch']
        }),
        ('Время приема', {
            'fields': ['date', 'time']
        }),
        ('Статус', {
            'fields': ['status']
        }),
        ('Даты', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    @admin.display(description='Обновлено')
    def time_since_update(self, obj):
        if obj.updated_at:
            time_diff = timesince(obj.updated_at, timezone.now())
            return f"{time_diff} назад"
        return "—"
    list_display_links = ['id', 'user_profile']
    ordering = ['-date', '-time']

class BranchServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'branch', 'service', 'is_available', 'time_since_update']
    list_filter = ['is_available', 'branch', 'service', 'updated_at']
    fieldsets = [
        ('Связь отделения и услуги', {
            'fields': ['branch', 'service']
        }),
        ('Доступность', {
            'fields': ['is_available']
        }),
        ('Дата обновления', {
            'fields': ['updated_at'],
            'classes': ['collapse']
        }),
    ]
    readonly_fields = ['updated_at']
    @admin.display(description='Обновлено')
    def time_since_update(self, obj):
        if obj.updated_at:
            time_diff = timesince(obj.updated_at, timezone.now())
            return f"{time_diff} назад"
        return "—"
    list_display_links = ['id', 'is_available']
    ordering = ['-updated_at']

admin.site.register(Branch, BranchAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(BranchService, BranchServiceAdmin)