from django.views.generic import ListView, DetailView

from .models import Article, Category
from django.shortcuts import render
from django.core.paginator import Paginator

#Наследуемся от ListView класса, это представление будет обрабатывать наш список объектов.
class ArticleListView(ListView):
    #название нашей модели, Article
    model = Article
    #название нашего шаблона
    template_name = 'blog/articles_list.html'
    #переменная, в которой будем хранить список для вывода в шаблоне.
    context_object_name = 'articles'
    #пагинация на основе классов, котрый мы используем для главной странице и добавим ему парамтер
    paginate_by = 2
    #добавление заголовка странице через добавления context в представление
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context
    
#это представление для получения одного объекта из набора QuerySet, 
#получаемое по slug или же pk, не исключаются любые другие поля
class ArticleDetailView(DetailView):
    #наша модель статьи
    model = Article
    #название нашего кастомного шаблона
    template_name = 'blog/articles_detail.html'
    #представленная переменная в шаблоне
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #наш заголовок передаваемый в этот наш объект(self.object.title),
        #т.е наша статья, у которой мы получаем заголовок.
        context['title'] = self.object.title
        return context
    
class ArticleByCategoryListView(ListView):
    model = Article
    template_name = 'blog/articles_list.html'
    context_object_name = 'articles'
    category = None

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Article.objects.all().filter(category__slug=self.category.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Статьи из категории: {self.category.title}' 
        return context
    
def articles_list(request):
    articles = Article.objects.all()
    paginator = Paginator(articles, per_page=2)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    context = {'page_obj': page_object}
    return render(request, 'blog/articles_func_list.html', context)