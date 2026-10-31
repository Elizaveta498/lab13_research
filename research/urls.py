from django.urls import path
from . import views

app_name = 'research'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_research, name='add'),
    path('upload/', views.upload_file, name='upload'),
    path('export/', views.export_all, name='export'),
    path('files/', views.files_list, name='files'),
    path('files/<str:filename>/', views.file_detail, name='file_detail'),
    path('files/<str:filename>/download/', views.file_download, name='file_download'),
    path('files/<str:filename>/delete/', views.file_delete, name='file_delete'),
    
    path('search/', views.search_db, name='search'),
    path('edit/<int:pk>/', views.edit_research, name='edit'),
    path('delete/<int:pk>/', views.delete_research, name='delete'),
]