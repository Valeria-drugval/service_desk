from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Категория")
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Request(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        ACCEPTED = "accepted", "Принята"
        IN_PROGRESS = "in_progress", "В работе"
        COMPLETED = "completed", "Выполнена"
        CLOSED = "closed", "Закрыта"

    title = models.CharField(max_length=255, verbose_name="Тема заявки")
    description = models.TextField(verbose_name="Описание проблемы")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.NEW, verbose_name="Текущий статус")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_requests", verbose_name="Клиент")
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="worker_requests", verbose_name="Исполнитель")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self): return f"Заявка #{self.id}: {self.title}"
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

class RequestStatusLog(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="status_history", verbose_name="Заявка")
    old_status = models.CharField(max_length=30, verbose_name="Старый статус")
    new_status = models.CharField(max_length=30, verbose_name="Новый статус")
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Кто изменил")
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="Время изменения")
    comment = models.TextField(blank=True, verbose_name="Комментарий к смене статуса")

    def __str__(self): return f"{self.request} | {self.old_status} -> {self.new_status}"
    class Meta:
        verbose_name = "История статусов"
        verbose_name_plural = "Истории статусов"

# НОВАЯ МОДЕЛЬ ДЛЯ КОММЕНТАРИЕВ
class Comment(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="comments", verbose_name="Заявка")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата написания")

    def __str__(self): return f"Комментарий от {self.author.username} к заявке #{self.request.id}"
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"