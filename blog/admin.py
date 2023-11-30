from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Article, Category

# Register your models here.

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    """
    Админ-панель модели категорий
    """
    list_display = ('tree_actions', 'indented_title', 'id', 'title', 'slug')
    list_display_links = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Основная информация', {'fields': ('title', 'slug', 'parent')}),
        ('Описание', {'fields': ('description',)})
    )

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    #позволяет с помощью JS обрабатывать заголовок в реальном времени
    #конвертирует даже кириллицу.
    prepopulated_fields = {'slug': ('title',)} 