from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404

# Create your views here.

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 3
    # context_object_name = 'my_book_list'  # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='war')[:5]  # Get 5 books containing the title war
    # template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location

    # Overriding methods in class-based views
    # 例如，我們可以覆寫get_queryset（）方法，來更改返回的記錄列表。
    # 這比單獨設置queryset屬性更靈活，就像我們在前面的代碼片段中進行的那樣（儘管在這案例中沒有太大用處）：
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war


    # Overriding methods in class-based views
    # 我們還可以重寫get_context_data() 以便將其他上下文變數傳遞給模組 (例如，默認情況下傳遞書籍列表).
    # 下面的片段顯示瞭如何向上下文添加名為"some_data" 的變數（然後它將用作模組變數）
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context

    # 執行此操作時，務必遵循上面使用的模式：
    # 首先從我們的superclass中獲取現有內文。
    # 然後添加新的內文信息。
    # 然後返回新的（更新後）內文。


class BookDetailView(generic.DetailView):
    model = Book

    # Just to give you some idea of how this works, the code fragment below demonstrates how you would implement the class-based view as a function, if you were not using the generic class-based detail view.
    # def book_detail_view(request, primary_key):
    #     try:
    #         book = Book.objects.get(pk=primary_key)
    #     except Book.DoesNotExist:
    #         raise Http404('Book does not exist')
    #
    #     # from django.shortcuts import get_object_or_404
    #     # book = get_object_or_404(Book, pk=primary_key)
    #
    #     return render(request, 'catalog/book_detail.html', context={'book': book})
