from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required       # Part 8
from django.contrib.auth.mixins import LoginRequiredMixin       # Part 8
from django.contrib.auth.decorators import permission_required  # Part 9
import datetime
from .forms import RenewBookForm
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

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
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

# Part 8: 可以透過裝飾器 @login_required 確保該 view function 需要登入後才能訪問
# https://docs.djangoproject.com/en/2.0/topics/auth/default/#limiting-access-to-logged-in-users
@login_required
def my_view_login_required(request):
    context = {
        'num_books': 0,
        'num_instances': 0,
        'num_instances_available': 0,
        'num_authors': 0,
        'num_visits': 0,
    }
    return render(request, 'index.html', context=context)

# Part 8: 以 LoginRequiredMixin 限制 user login 後才能訪問 view class
class MyViewLoginRequired(LoginRequiredMixin, generic.ListView):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

# Part 8
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin

# Added as part of challenge!
class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')



from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import permission_required

# from .forms import RenewBookForm
from catalog.forms import RenewBookForm

# Part 9
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})



# renew_book_librarian用於讀書館員幫讀者手動更新書的到期日
# ****************改用modelform的方式實做！***********
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

# 用modelform方式實做的話，與之前的差異點：需改 import RenewBookModelForm
# from .forms import RenewBookForm
from .forms import RenewBookModelForm


def renew_book_librarian_modelform(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':

        # 用modelform方式實做的話，與之前的差異點：需改用RenewBookModelForm去做欄位驗證
        # form = RenewBookForm(request.POST)
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # 用modelform方式實做的話，與之前的差異點：欄位名稱需改成due_back
            # book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.due_back = form.cleaned_data['due_back']
            book_inst.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)

        # 用modelform方式實做的話，與之前的差異點：欄位名稱需改成due_back
        # form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})
        form = RenewBookModelForm(initial={'due_back': proposed_renewal_date, })

    return render(request, 'catalog/book_renew_librarian_modelform.html', {'form': form, 'bookinst': book_inst})



#modelform實做範例
#利用Django的skeleton快速建立create, update, delete功能
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    #選取Author資料表全部的欄位
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}

class AuthorUpdate(UpdateView):
    model = Author
    #選取特定欄位
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    #刪除成功之後，自動導向到下列的網址
    success_url = reverse_lazy('authors')



#建立Author資料的List清單網頁
from django.views import generic

#這是class-based views的限制網頁必須登入的作法
from django.contrib.auth.mixins import LoginRequiredMixin

class AuthorListView(LoginRequiredMixin, generic.ListView):
# class AuthorListView(generic.ListView):
    model = Author
    #透過定義get_queryset()就可以自己定義想要的資料
    #沒有要自定義的話就註解掉get_queryset()
    def get_queryset(self):
        # return Author.objects.filter(title__icontains='bike')[:5] #取前五筆資料，title包含關鍵字'bike'的
        return Author.objects.filter()[:100] #取前100筆資料
    #等等要去哪個路徑找.html檔案
    #不定義這個template_name的話，Django就會去預設的路徑尋找.html
    #預設的路徑是：/locallibrary/catalog/templates/catalog/author_list.html
    #不過目前暫時程式碼設定路徑的方式跟預設一樣就好
    template_name = '/locallibrary/catalog/templates/catalog/author_list.html'

    #get_context_data()是用來建立自訂的Server side variable的
    #跟.Net MVC也挺像的
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context

    #這是分頁機制, 以下設定每頁最多10筆資料
    paginate_by = 10

