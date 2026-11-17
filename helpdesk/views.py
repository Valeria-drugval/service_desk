from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import psutil
import os

from .models import Request, Category, Comment
from .services import RequestService

@login_required
def request_list(request):
    if request.user.is_staff:
        requests = Request.objects.all().order_by('-created_at')
    else:
        requests = Request.objects.filter(client=request.user).order_by('-created_at')
    
    # Данные для пончика (статусы)
    status_counts = requests.values('status').annotate(count=Count('id'))
    pie_labels = []
    pie_data = []
    for item in status_counts:
        pie_labels.append(dict(Request.Status.choices).get(item['status']))
        pie_data.append(item['count'])

    # Данные для линейного графика (за последние 7 дней)
    today = timezone.now().date()
    line_labels = []
    line_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        line_labels.append(day.strftime('%d.%m'))
        line_data.append(requests.filter(created_at__date=day).count())

    context = {
        'requests': requests,
        'total_count': requests.count(),
        'in_progress_count': requests.filter(status=Request.Status.IN_PROGRESS).count(),
        'completed_count': requests.filter(status=Request.Status.COMPLETED).count(),
        'closed_count': requests.filter(status=Request.Status.CLOSED).count(),
        'pie_labels': pie_labels,
        'pie_data': pie_data,
        'line_labels': line_labels,
        'line_data': line_data,
    }
    return render(request, 'helpdesk/request_list.html', context)

@login_required
def create_request(request):
    if request.method == 'POST':
        Request.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            category_id=request.POST.get('category'),
            client=request.user
        )
        messages.success(request, 'Заявка успешно создана!')
        return redirect('request_list')
    return render(request, 'helpdesk/create_request.html', {'categories': Category.objects.all()})

@login_required
def request_detail(request, pk):
    req = get_object_or_404(Request, pk=pk)
    next_statuses = RequestService.ALLOWED_TRANSITIONS.get(req.status, [])
    next_statuses_display = [(status, Request.Status(status).label) for status in next_statuses]
    
    return render(request, 'helpdesk/request_detail.html', {
        'req': req, 
        'next_statuses': next_statuses_display
    })

@login_required
def change_status(request, pk, new_status):
    req = get_object_or_404(Request, pk=pk)
    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        if RequestService.change_status(req, new_status, request.user, comment):
            messages.success(request, f'Статус изменен на: {Request.Status(new_status).label}')
        else:
            messages.error(request, 'Ошибка: недопустимый переход статуса!')
    return redirect('request_detail', pk=pk)

# API ДЛЯ ТЕЛЕМЕТРИИ (CPU, RAM, DISK)
@login_required
def api_telemetry(request):
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    
    return JsonResponse({
        'cpu': cpu,
        'ram': ram,
        'disk': disk
    })

# ДОБАВЛЕНИЕ КОММЕНТАРИЯ
@login_required
def add_comment(request, pk):
    req = get_object_or_404(Request, pk=pk)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Comment.objects.create(request=req, author=request.user, text=text)
            messages.success(request, 'Комментарий добавлен!')
    return redirect('request_detail', pk=pk)