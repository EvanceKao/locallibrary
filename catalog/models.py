from django.db import models
from django.urls import reverse                 # To generate URLS by reversing URL patterns
import uuid                                     # Required for unique book instances
from django.contrib.auth.models import User     # Part 8
from datetime import date                       # Part 8

# Create your models here.
class MyModelName(models.Model):
    """A typical class defining a model, derived from the Model class."""

    # Fields
    my_field_name = models.CharField(max_length=20, help_text='Enter field documentation')
    ...

    # Metadata
    class Meta:
        # 前綴加上 "-" ，代表反轉排序順序
        ordering = ['-my_field_name']
        # 下面的 ordering 代表：書單通過標題依據--字母排序--排列，從A到Z，然後再依每個標題的出版日期，從最新到最舊排列。
        # ordering = ['title', '-pubdate']

    # Methods
    def get_absolute_url(self):
        """Returns the url to access a particular instance of MyModelName."""
        return reverse('model-detail-view', args=[str(self.id)])

    # 最起碼，在每個模型中，你應該定義標準的Python 類方法__str__() ，來為每個物件返回一個人類可讀的字符串。
    def __str__(self):
        """String for representing the MyModelName object (in Admin site etc.)."""
        return self.field_name

# 書籍類型模型 (Genre model)
# 「書籍類別」(genre)是一個 ManyToManyField ，因此一本書可以有很多書籍類別，而一個書籍類別也能夠對應到很多本書。
class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name

# 書本模型 (Book model)
class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)

    # 作者(author)被宣告為外鍵(ForeignKey)，因此每本書只會有一名作者，但一名作者可能會有多本書
    # (實際上，一本書可能會有多名作者，不過這個案例不會有，所以在別的例子這種作法可能會有問題)
    # null=True 表示如果沒有作者的話，允許在資料庫中存入 Null 值
    # on_delete=models.SET_NULL 表示如果某筆作者紀錄被刪除的話，與該作者相關連的欄位都會被設成 Null。
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file.
    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')

    # 這個模型也定義了 __str__() ，使用書本的 title 字段來表示一筆 Book 的紀錄。
    def __str__(self):
        """String for representing the Model object."""
        return self.title

    # 而最後一個方法，get_absolute_url() ，則會回傳一個可以被用來存取該模型細節紀錄的 URL
    # (要讓其有效運作，我們必須定義一個 URL 的映射，我們將其命名為 book-detail ，另外還得定義一個關聯示圖(view)與模板(template) )。
    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

    # 這會從genre記錄的的頭三個值（如果有的話）創建一個字符串, 和創建一個在管理者網站中出現的short_description標題。
    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'

# 書本詳情模型 (BookInstance model)
class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""

    # UUIDField 被用來將 id 字段再這個模型中設定為 primary_key ，這類別的字段會分配一個全域唯一的值給每一個實例(instance)，也就是任何一本你能在圖書館找到的書。
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    # DateField 會被用來設定 due_back 的日期(紀錄書本何時會被歸還，可再被使用，或者是否正在保養期)，這個字段允許 blank 或 null 值，而當元數據模型 (Class Meta)收到請求(query)時也會使用此字段來做資料排序。
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    # status 是一個 CharField 字段，用來定義一個選項列表。你可以看到，我們定義了一個包含「鍵-值對元組」的元組(tuple) 並使其成為選項的參數，鍵-值對中的值會陳列出來並可以被使用者選擇，當選項被選定後，鍵(key)也會被儲存下來。我們也設定了預設的鍵值為 "m" (maintenance) 用來表示當每本書在初始創造還未放上書架時是不可被使用的。
    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    # 而 __str__() 模型用來表示 BookInstance 這個物件的「唯一 ID」和「相關之 Book 書本名稱(title)」的組合。
    def __str__(self):
        """String for representing the Model object."""
        # 從 Python3.6 開始，你可以使用「字串插值語法」(又稱做 f-string)：
        return f'{self.id} ({self.book.title})'
        # 在舊版 Python 這部分的教學中，我們則使用了另一種有效的 formatted string 語法
        # (e.g. '{0} ({1})'.format(self.id,self.book.title))

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

# 作者模型(Author model)
class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    # def get_absolute_url(self):
    #     """Returns the url to access a particular author instance."""
    #     return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'



