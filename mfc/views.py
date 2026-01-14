from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages  # для показа сообщений пользователю
from django.core.exceptions import ValidationError
from .models import Branch

def branch_list(request):
    branches = Branch.objects.all().order_by('name')
    return render(request, 'mfc/branch_list.html', {'branches': branches})

def branch_detail(request, pk):
    branch = get_object_or_404(Branch, pk=pk) # пытаемся найти запись в базе
    return render(request, 'mfc/branch_detail.html', {'branch': branch})


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
        if not address:
            errors.append("Адрес обязателен для заполнения.")
        if not phone:
            errors.append("Телефон обязателен для заполнения.")
        if not email:
            errors.append("Email обязателен для заполнения.")
        if not work_schedule:
            errors.append("График работы обязателен для заполнения.")

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
        if not address:
            errors.append("Адрес обязателен для заполнения.")
        if not phone:
            errors.append("Телефон обязателен для заполнения.")
        if not email:
            errors.append("Email обязателен для заполнения.")
        if not work_schedule:
            errors.append("График работы обязателен для заполнения.")
        
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
