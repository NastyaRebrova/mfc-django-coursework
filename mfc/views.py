from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Branch, Service, BranchService, Appointment
from datetime import datetime
import re
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Avg
from math import ceil

def branch_list(request):
    branches = Branch.objects.all().order_by('name').annotate(
        services_count=Count('branch_services', distinct=True),   
        avg_duration_days=Avg('services__duration_days'), 
    )
    for branch in branches:
        if branch.avg_duration_days:
            branch.avg_duration_days = ceil(branch.avg_duration_days)
    
    return render(request, 'mfc/branch_list.html', {'branches': branches})

def branch_detail(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    services = BranchService.objects.filter(
        branch=branch
    ).select_related('service')
    return render(request, 'mfc/branch_detail.html', {
        'branch': branch,
        'services': services,
    })
@staff_member_required
def branch_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        work_schedule = request.POST.get('work_schedule', '').strip()
        photo = request.FILES.get('photo')

        errors = []
        if not name:
            errors.append("Название отделения обязательно для заполнения.")
        elif len(name) < 3:
            errors.append("Название отделения должно содержать минимум 3 символа")
        
        if not address:
            errors.append("Адрес обязателен для заполнения.")
        elif len(address) < 10:
            errors.append("Адрес должен содержать минимум 10 символов")
        
        if not phone:
            errors.append("Телефон обязателен для заполнения")
        
        if not email:
            errors.append("Email обязателен для заполнения.")
        else:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                errors.append("Введите корректный email адрес (например: office@mfc.ru)")
        
        if not work_schedule:
            errors.append("График работы обязателен для заполнения")
        elif len(work_schedule) < 10:
            errors.append("График работы должен содержать подробное описание")
        
        if email and Branch.objects.filter(email=email).exists():
            errors.append("Отделение с таким email уже существует")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'mfc/branch_form.html', {'form_type': 'create'})
         
        try:
            branch = Branch.objects.create(
                name=name,
                address=address,
                phone=phone,
                email=email,
                work_schedule=work_schedule,
                is_active=True 
            )
            
            if photo:
                if photo.size > 5 * 1024 * 1024:  # 5MB в байтах
                    messages.warning(request, "Фото слишком большое (максимум 5MB).")
                else:
                    branch.photo = photo
                    branch.save()
            
            messages.success(request, f'Отделение "{name}" успешно создано!')
            return redirect('mfc:branch_detail', pk=branch.pk)
            
        except Exception:
            messages.error(request, 'Произошла ошибка при создании отделения.')
            return render(request, 'mfc/branch_form.html', {'form_type': 'create'})
    
    else: # GET запрос
        return render(request, 'mfc/branch_form.html', {'form_type': 'create'})

@staff_member_required
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        work_schedule = request.POST.get('work_schedule', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        photo = request.FILES.get('photo')
        photo_clear = request.POST.get('photo-clear') == '1'
        
        errors = []
        if not name:
            errors.append("Название отделения обязательно для заполнения.")
        elif len(name) < 3:
            errors.append("Название отделения должно содержать минимум 3 символа")
        
        if not address:
            errors.append("Адрес обязателен для заполнения.")
        elif len(address) < 10:
            errors.append("Адрес должен содержать минимум 10 символов")
        
        if not phone:
            errors.append("Телефон обязателен для заполнения")
        
        if not email:
            errors.append("Email обязателен для заполнения.")

        if not work_schedule:
            errors.append("График работы обязателен для заполнения")
        elif len(work_schedule) < 10:
            errors.append("График работы должен содержать подробное описание")
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'mfc/branch_form.html', {'branch': branch, 'form_type': 'edit'})
        
        try:
            branch.name = name
            branch.address = address
            branch.phone = phone
            branch.email = email
            branch.work_schedule = work_schedule
            branch.is_active = is_active
            
            if photo_clear and branch.photo:
                branch.photo.delete(save=False)
                branch.photo = None
            
            if photo:
                if photo.size > 5 * 1024 * 1024:
                    messages.warning(request, "Фото слишком большое (максимум 5MB).")
                else:
                    if branch.photo:
                        branch.photo.delete(save=False)
                    branch.photo = photo
            
            branch.save()
            messages.success(request, f'Отделение "{name}" успешно обновлено!')
            return redirect('mfc:branch_detail', pk=branch.pk)
            
        except Exception:
            messages.error(request, 'Произошла ошибка при обновлении.')
            return render(request, 'mfc/branch_form.html', {'branch': branch, 'form_type': 'edit'})
    
    else:
        return render(request, 'mfc/branch_form.html', {
            'branch': branch,
            'form_type': 'edit'
        })

@staff_member_required
def branch_delete(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == 'POST':
        try:
            branch_name = branch.name
            
            if branch.photo:
                branch.photo.delete(save=False)
            
            branch.delete()
            messages.success(request, f'Отделение "{branch_name}" успешно удалено!')
            return redirect('mfc:branch_list')
            
        except Exception as e:
            messages.error(request, f'Произошла ошибка при удалении: {str(e)}')
            return redirect('mfc:branch_detail', pk=pk)
    
    else:
        return render(request, 'mfc/branch_confirm_delete.html', {'branch': branch})

@login_required
def appointment_create(request, branch_pk):
    branch = get_object_or_404(Branch, pk=branch_pk)
    if request.user.is_staff:
        messages.error(
            request, 
            'Администраторы не могут записываться на услуги. Эта функция доступна только клиентам.'
        )
        return redirect('mfc:branch_detail', pk=branch.pk)
    if not branch.is_active:
        messages.error(
            request, 
            f'Отделение "{branch.name}" в настоящее время неактивно. Запись невозможна.'
        )
        return redirect('mfc:branch_detail', pk=branch.pk)
    available_services = BranchService.objects.filter(
        branch=branch,           
        is_available=True        
    ).select_related('service') 
    
    if request.method == 'POST':
        service_id = request.POST.get('service')
        date_str = request.POST.get('date')       
        time_str = request.POST.get('time')
        
        errors = []
        
        if not service_id:
            errors.append("Выберите услугу из списка")
        
        if not date_str:
            errors.append("Укажите дату приема")
        
        if not time_str:
            errors.append("Укажите время приема")
        
        if date_str:
            try:
                # преобразуем строку в объект date
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if selected_date < timezone.now().date():
                    errors.append("Дата не может быть в прошлом. Выберите сегодняшнюю или будущую дату.")
                    
            except ValueError:
                errors.append("Неверный формат даты. Используйте формат ГГГГ-ММ-ДД.")
        
        if time_str:
            try:
                selected_time = datetime.strptime(time_str, '%H:%M').time()
                hour = selected_time.hour
                minute = selected_time.minute
                if hour < 9 or (hour == 18 and minute > 0) or hour > 18:
                    errors.append(
                        "Время приема должно быть в рабочее время (с 9:00 до 18:00). "
                        "Пожалуйста, выберите время в этом диапазоне."
                    )
                    
            except ValueError:
                errors.append("Неверный формат времени. Используйте формат ЧЧ:ММ.")
        
        if errors:
            # перебираем все ошибки и добавляем их как сообщения
            for error in errors:
                messages.error(request, error)
            return render(request, 'mfc/appointment_form.html', {
                'branch': branch,
                'available_services': available_services,
                'selected_service': service_id,     
                'selected_date': date_str,          
                'selected_time': time_str,           
            })
        
        try:
            service = get_object_or_404(Service, pk=service_id)
            appointment = Appointment.objects.create(
                user_profile=request.user.userprofile, 
                service=service,                        
                branch=branch,                        
                date=date_str,                      
                time=time_str,                         
                status=Appointment.Status.PENDING       
            )
            
            # показываем пользователю сообщение об успехе
            messages.success(
                request, 
                f'Вы успешно записаны на услугу "{service.name}" '
                f'в отделении "{branch.name}" на {date_str} в {time_str}!'
            )
            
            return redirect('mfc:branch_detail', pk=branch.pk)
            
        except Exception as e:
            messages.error(
                request, 
                f'Произошла непредвиденная ошибка при записи: {str(e)}. '
                'Пожалуйста, попробуйте еще раз или обратитесь к администратору.'
            )
            
            return render(request, 'mfc/appointment_form.html', {
                'branch': branch,
                'available_services': available_services,
                'selected_service': service_id,
                'selected_date': date_str,
                'selected_time': time_str,
            })
    
    return render(request, 'mfc/appointment_form.html', {
        'branch': branch,
        'available_services': available_services,
    })