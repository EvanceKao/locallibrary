from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    # This method is used just like path() except that it allows you to specify a pattern using a Regular expression.
    # For example, the previous path could have been written as shown below:
    # re_path(r'^book/(?P<pk>\d+)$', views.BookDetailView.as_view(), name='book-detail'),
]

urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]

#圖書館管理人員限定的 更新讀者書本到期日的功能
#網址格式：/catalog/book/<bookinstance id>/renew/
#renew_book_librarian是底線分隔，表示這是一個function-based view
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

#圖書館管理人員限定的 更新讀者書本到期日的功能(改用modelform的方式實做)
#網址格式：/catalog/book/<bookinstance id>/renew_bymodelform/
#renew_book_librarian是底線分隔，表示這是一個function-based view
urlpatterns += [
    path('book/<uuid:pk>/renew_bymodelform/', views.renew_book_librarian_modelform, name='renew-book-librarian-modelform'),
]



#modelform實做範例
#Author資料利用modelform快速建立create, update, delete功能
#modelform的快速建立功能相當類似asp.net mvc的skeleton
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author_create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author_update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author_delete'),
]

#加入Authors資料表的list清單網頁的url mapping
urlpatterns += [
    path('authors/', views.AuthorListView.as_view(), name='authors'),
]



