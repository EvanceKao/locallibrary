from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

# Register your models here.
# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)

# 註冊 模型管理 類別 (ModelAdmin class)
# 然後再 配置列表視圖(Configure list views)

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    # pass
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    # fields 屬性僅按順序列出了要在表單上顯示的那些欄位。 默認情況下，字段是垂直顯示的，但是如果您進一步將它們分組到一個元組中，它們將水平顯示
    # （如上面的“日期”字段中所示）。
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    # 還可以使用 exclude 屬性來聲明要從表單中排除的屬性列表（將顯示模型中的所有其他屬性）。

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

# Inline editing of associated records
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance

# 現在我們要創造並註冊新的模型；為了達到示範的目的，我們會使用 @register 裝飾器替代先前做法來註冊模型
# (這跟 admin.site.register() 的語法做的事情完全一樣)：
# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # pass
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    # pass
    # 當你的列表有很多個記錄時, 加入列表過濾器可以幫助你過濾想顯示的記錄。加入list_filter這個屬性就可以。
    list_filter = ('status', 'due_back')

    # Sectioning the detail view
    # You can add "sections" to group related model information within the detail form, using the fieldsets attribute.
    # In the BookInstance model we have information related to what the book is (i.e. name, imprint, and id) and when it will be available (status, due_back). We can add these in different sections by adding the text in bold to our BookInstanceAdmin class.
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )
    # Each section has its own title (or None, if you don't want a title) and an associated tuple of fields in a dictionary — the format is complicated to describe, but fairly easy to understand if you look at the code fragment immediately above.





