from rest_framework import serializers
from django.core.validators import EmailValidator, RegexValidator
from .models import Branch, Service

class BranchSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
                message="Телефон введен в некорректном формате"
            )
        ]
    )

    email = serializers.EmailField(
        validators=[
            EmailValidator(message="Введите корректный email адрес")
        ]
    )

    name = serializers.CharField(
        max_length=200,
        min_length=3,
        error_messages={
            'min_length': 'Название должно содержать минимум 3 символа',
            'max_length': 'Название не должно превышать 200 символов'
        }
    )

    photo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Branch
        fields = [
            'id', 'name', 'address', 'phone', 'email', 
            'photo', 'photo_url', 'work_schedule', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'photo_url']

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None
    
    def validate_work_schedule(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                "График работы должен содержать подробное описание"
            )
        return value 
    
    def validate(self, data):
        email = data.get('email')
        instance = self.instance
        # при создании нового отделения
        if not instance and Branch.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                'email': 'Отделение с таким email уже существует'
            })
        # при обновлении существующего отделения
        if instance and Branch.objects.filter(email=email).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({
                'email': 'Отделение с таким email уже существует'
            })
        return data
    
class ServiceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=200,
        min_length=5,
        error_messages={
            'min_length': 'Название услуги должно содержать минимум 5 символов',
            'max_length': 'Название услуги не должно превышать 200 символов'
        }
    )
    
    duration_days = serializers.IntegerField(
        min_value=1,
        max_value=365,
        error_messages={
            'min_value': 'Срок выполнения не может быть меньше 1 дня',
            'max_value': 'Срок выполнения не может превышать 365 дней'
        }
    )

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'category', 'duration_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        instance = self.instance
        
        if not instance and Service.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Услуга с таким названием уже существует"
            )
        
        if instance and Service.objects.filter(name=value).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError(
                "Услуга с таким названием уже существует"
            )
        
        return value