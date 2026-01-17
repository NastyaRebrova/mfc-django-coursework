# как использовать:
#     python manage.py generate_test_services
#     python manage.py generate_test_services --count 10
#     python manage.py generate_test_services --categories DOC,TRANS,SOC

from django.core.management.base import BaseCommand
from mfc.models import Service

class Command(BaseCommand):
    help = 'Создает тестовые услуги для системы МФЦ'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Количество услуг для создания (по умолчанию: 5)'
        )
        
        parser.add_argument(
            '--categories',
            type=str,
            default='DOC,TRANS,SOC',
            help='Категории услуг через запятую (по умолчанию: DOC,TRANS,SOC)'
        )
    
    def handle(self, **options):
        count = options['count']
        categories_str = options['categories']
        categories = [c.strip() for c in categories_str.split(',')]
    
        test_services = [
            {'name': 'Загранпаспорт', 'category': 'DOC', 'duration': 30},
            {'name': 'Свидетельство о рождении', 'category': 'DOC', 'duration': 7},
            {'name': 'Справка о несудимости', 'category': 'DOC', 'duration': 10},
            
            {'name': 'Водительское удостоверение', 'category': 'TRANS', 'duration': 15},
            {'name': 'Регистрация транспортного средства', 'category': 'TRANS', 'duration': 5},
            {'name': 'Международные права', 'category': 'TRANS', 'duration': 20},
            
            {'name': 'Пенсионное удостоверение', 'category': 'SOC', 'duration': 7},
            {'name': 'Социальная карта', 'category': 'SOC', 'duration': 21},
            {'name': 'Пособие по безработице', 'category': 'SOC', 'duration': 10},
            
            {'name': 'Свидетельство о собственности', 'category': 'PROP', 'duration': 30},
            {'name': 'Дарственная на квартиру', 'category': 'PROP', 'duration': 45},
            {'name': 'Ипотечная регистрация', 'category': 'PROP', 'duration': 20},

            {'name': 'Регистрация ИП', 'category': 'BUS', 'duration': 5},
            {'name': 'Открытие расчетного счета', 'category': 'BUS', 'duration': 3},
            {'name': 'Лицензия на торговлю', 'category': 'BUS', 'duration': 30},

            {'name': 'Медицинская справка', 'category': 'HLTH', 'duration': 1},
            {'name': 'Больничный лист', 'category': 'HLTH', 'duration': 3},
            {'name': 'Справка для бассейна', 'category': 'HLTH', 'duration': 2},
            
            {'name': 'Аттестат о среднем образовании', 'category': 'EDU', 'duration': 30},
            {'name': 'Академическая справка', 'category': 'EDU', 'duration': 15},
            {'name': 'Справка об обучении', 'category': 'EDU', 'duration': 5},
            
            {'name': 'Консультация юриста', 'category': 'OTHER', 'duration': 1},
            {'name': 'Нотариальное заверение', 'category': 'OTHER', 'duration': 1},
            {'name': 'Перевод документов', 'category': 'OTHER', 'duration': 3},
        ]
        
        # фильтруем услуги по выбранным категориям
        filtered_services = [s for s in test_services if s['category'] in categories]
        
        if not filtered_services:
            self.stdout.write(self.style.ERROR('Нет услуг для выбранных категорий'))
            self.stdout.write('Доступные категории: DOC, TRANS, SOC, PROP, BUS, HLTH, EDU, OTHER')
            return
        
        services_to_create = filtered_services[:count]
        
        self.stdout.write('Создание тестовых услуг МФЦ')
        self.stdout.write('=' * 50)
        self.stdout.write(f'Будут созданы услуги: {len(services_to_create)} из {len(filtered_services)} доступных')
        self.stdout.write(f'Категории: {", ".join(categories)}')
        self.stdout.write('')
        
        created_count = 0
        for service_data in services_to_create:
            # проверяем не существует ли уже такая услуга
            if not Service.objects.filter(name=service_data['name']).exists():
                service = Service.objects.create(
                    name=service_data['name'],
                    category=service_data['category'],
                    duration_days=service_data['duration']
                )
                created_count += 1
                self.stdout.write(f'Создана: {service.name} ({service.get_category_display()}, {service.duration_days} дней)')
            else:
                self.stdout.write(f'Уже существует): {service_data["name"]}')
        