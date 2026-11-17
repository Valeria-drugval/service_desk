from django.contrib import admin
from .models import Category, Request, RequestStatusLog, Comment

class RequestStatusLogInline(admin.TabularInline):
    model = RequestStatusLog
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'changed_at')
    can_delete = False

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'client', 'assignee', 'status', 'created_at')
    list_filter = ('status', 'category')
    inlines = [RequestStatusLogInline, CommentInline]

admin.site.register(Category)