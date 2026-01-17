from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class Branch(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название отделения"
    )
    
    address = models.TextField(
        verbose_name="Адрес"
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон"
    )
    
    email = models.EmailField(
        verbose_name="Email адрес"
    )
    
    photo = models.ImageField(
        upload_to='branches/',
        verbose_name="Фото отделения",
        blank=True, # поле может быть пустым в форме
        null=True
    )
    
    work_schedule = models.TextField(
        verbose_name="График работы"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Отделение"
        
        verbose_name_plural = "Отделения"
        
        ordering = ['name']
        
        # для ускорения поиска
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.address})"
    
class Service(models.Model):
    class Category(models.TextChoices):
        DOCUMENTS = 'DOC', 'Документы и справки'
        PROPERTY = 'PROP', 'Недвижимость и земля'
        TRANSPORT = 'TRANS', 'Транспорт и водительские права'
        SOCIAL = 'SOC', 'Социальные услуги'
        BUSINESS = 'BUS', 'Бизнес и предпринимательство'
        HEALTH = 'HLTH', 'Здравоохранение'
        EDUCATION = 'EDU', 'Образование'
        OTHER = 'OTHER', 'Прочее'
    
    name = models.CharField(
        max_length=200,
        verbose_name="Название услуги"
    )
    
    category = models.CharField(
        max_length=10,
        choices=Category.choices,
        default=Category.OTHER,
        verbose_name="Категория"
    )
    
    duration_days = models.PositiveIntegerField(
        default=14,
        verbose_name="Срок выполнения",
        help_text="Сколько дней занимает оказание услуги"
    )

    branches = models.ManyToManyField(
        Branch,                   
        through='BranchService',    
        verbose_name="Доступна в отделениях",
        related_name='services',     # branch.services.all() 
        blank=True        
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Услуга"

        verbose_name_plural = "Услуги"
        
        ordering = ['name']
        
        indexes = [
            models.Index(fields=['category'])
        ]
    
    def __str__(self):
        return self.name

class BranchService(models.Model):
    branch = models.ForeignKey(
        Branch,                   
        on_delete=models.CASCADE,   
        verbose_name="Отделение", 
        related_name='branch_services'  # обратная связь: branch.branch_services.all()
    )

    service = models.ForeignKey(
        Service,               
        on_delete=models.CASCADE, 
        verbose_name="Услуга",
        related_name='branch_services'
    )
    
    is_available = models.BooleanField(
        default=True,
        verbose_name="Доступна в отделении"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления доступности"
    )
    
    class Meta:
        verbose_name = "Доступность услуги в отделении"

        verbose_name_plural = "Доступность услуг в отделениях"
        
        unique_together = ['branch', 'service'] # уникальность комбинации полей
        
        indexes = [
            models.Index(fields=['branch']),
            models.Index(fields=['service']),
            models.Index(fields=['branch', 'is_available']),
            models.Index(fields=['service', 'is_available']),
        ]
        
        ordering = ['branch__name', 'service__name']  # сначала по названию отделения, потом услуги
    
    def __str__(self):
        status = "Доступна" if self.is_available else "Недоступна"
        return f"{self.service.name} в {self.branch.name} ({status})"
    
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Клиент'),
        ('employee', 'Сотрудник МФЦ'),
        ('admin', 'Администратор системы'),
    ]
    
    user = models.OneToOneField( # связь 1:1 с встроенным User
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name='userprofile'
    )
    
    full_name = models.CharField(
        max_length=200,
        verbose_name="Полное имя",
    )
    
    email = models.EmailField(
        verbose_name="Email",
        unique=True
    )
    
    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name="Роль"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Профиль пользователя"

        verbose_name_plural = "Профили пользователей"

        ordering = ['full_name']
        
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.user.email:
            self.user.email = self.email
            self.user.save()
        super().save(*args, **kwargs)

class Employee(models.Model):
    POSITION_CHOICES = [
        ('specialist', 'Специалист приема'),
        ('consultant', 'Консультант'),
        ('admin', 'Администратор отделения'),
    ]
    
    user_profile = models.OneToOneField( # связь 1:1 с UserProfile
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="Профиль пользователя",
        related_name='employee_profile',
    )
    
    office = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        verbose_name="Отделение МФЦ",
        related_name='employees',
    )
    
    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        verbose_name="Должность",
        default='specialist',
        help_text="Должность сотрудника МФЦ"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата приема на работу"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения данных"
    )
    
    class Meta:
        verbose_name = "Сотрудник МФЦ"
        
        verbose_name_plural = "Сотрудники МФЦ"
        
        ordering = ['user_profile__full_name']
        
        indexes = [
            models.Index(fields=['position']),
            models.Index(fields=['office']),
            models.Index(fields=['user_profile']),
        ]
    
    def __str__(self):
        office_name = self.office.name
        return f"{self.user_profile.full_name} - {self.get_position_display()} ({office_name})"
    
    def save(self, *args, **kwargs):
        if self.user_profile.role != 'employee':
            self.user_profile.role = 'employee'
            self.user_profile.save()
        super().save(*args, **kwargs)

class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Ожидает'
        CONFIRMED = 'CONFIRMED', 'Подтверждена'
        IN_PROGRESS = 'IN_PROGRESS', 'В работе'
        COMPLETED = 'COMPLETED', 'Завершена'
        CANCELLED = 'CANCELLED', 'Отменена'
        NO_SHOW = 'NO_SHOW', 'Не явился'
    
    user_profile = models.ForeignKey(
        'UserProfile', 
        on_delete=models.CASCADE, 
        verbose_name="Профиль пользователя",
        related_name='appointments' 
    )
    
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name="Услуга",
        related_name='appointments' 
    )
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        verbose_name="Отделение",
        related_name='appointments'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус"
    )
    
    date = models.DateField(
        verbose_name="Дата приема"
    )
    
    time = models.TimeField(
        verbose_name="Время приема",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания записи"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Запись на прием"
        verbose_name_plural = "Записи на прием"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['date']),
            models.Index(fields=['user_profile']),
            models.Index(fields=['branch', 'date']),
            models.Index(fields=['branch', 'status', 'date']),
        ]
    
    def __str__(self):
        user_name = self.user_profile.full_name or self.user_profile.user.username
        return f"Запись #{self.id}: {user_name} - {self.date} {self.time}"