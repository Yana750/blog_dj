from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey

from blog.services.utils import unique_slugify

# Create your models here.

#это удобный способ получить модель пользователя, определенную в проекте Django. 
#Вместо того, чтобы явно импортировать модель пользователя
#возвращает модель пользователя, которая настроена в настройках проекта (AUTH_USER_MODEL).
User = get_user_model()

class Article(models.Model):
    """
    Модель постов для сайта
    """

    class ArticleManager(models.Manager):
        """
        Кастомный менеджер для модели статей
        """

        def all(self):
            """
            Список статей (SQL запрос с фильтрацией для страницы списка статей)
            """
            return self.get_queryset().select_related('author', 'category').filter(status='published')

    STATUS_OPTIONS = (
        ('published', 'Опубликовано'), 
        ('draft', 'Черновик')
    )

    #заголовок, с максимальным количеством символов 255
    title = models.CharField(verbose_name='Заголовок', max_length=255)
    #ссылка на материал (латиница), или в простонародии ЧПУ-человеко-понятный урл
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    #категории 
    category = TreeForeignKey('Category', on_delete=models.PROTECT, related_name='articles', verbose_name='Категория')
    #текстовое поле, ограниченное 300 символами.
    short_description = models.TextField(verbose_name='Краткое описание', max_length=500)
    #аналогично, без ограничений
    full_description = models.TextField(verbose_name='Полное описание')
    #превью статьи.
    thumbnail = models.ImageField(
        verbose_name='Превью поста', 
        blank=True, 
        upload_to='images/thumbnails/%Y/%m/%d/', 
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))]
    )
    #опубликована статья, или черновик
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус поста', max_length=10)
    #время создания и обновления статьи.
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    #ключ ссылаемый на пользователя из другой таблицы (пользователей) c on_delete=models.PROTECT
    author = models.ForeignKey(to=User, verbose_name='Автор', on_delete=models.SET_DEFAULT, related_name='author_posts', default=1)
    #налогично, только если при обновлении статьи выводить того, кто редактировал (добавлять, если вам это нужно) c on_delete=models.CASCADE
    updater = models.ForeignKey(to=User, verbose_name='Обновил', on_delete=models.SET_NULL, null=True, related_name='updater_posts', blank=True)
    #булево значение, по умолчанию False (не закреплено)
    fixed = models.BooleanField(verbose_name='Зафиксировано', default=False)

    

    class Meta:
        db_table = 'app_articles'
        ordering = ['-fixed', '-time_create']
        indexes = [models.Index(fields=['-fixed', '-time_create', 'status'])]
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    custom = ArticleManager()
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('articles_detail', kwargs={'slug': self.slug}) 
    
    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

class Category(MPTTModel):
    """
    Модель категорий с вложенностью
    """
    title = models.CharField(max_length=255, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, verbose_name='URL категории', blank=True)
    description = models.TextField(verbose_name='Описание категории', max_length=300)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Родительская категория'
    )

    class MPTTMeta:
        """
        Сортировка по вложенности, наследуемся от MPTTModel
        """
        order_insertion_by = ('title',)

    class Meta:
        """
        Сортировка, название модели в админ панели, таблица в данными
        """
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'app_categories'

    def __str__(self):
        """
        Возвращение заголовка статьи
        """
        return self.title
    
    def get_absolute_url(self):
        return reverse('articles_by_category', kwargs={'slug': self.slug})