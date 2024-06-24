from django.urls import path
from . import views

urlpatterns = [
    path('generate-update-list/', views.generate_update_list_view, name='generate_update_list'),
    path('store-files-in-db/', views.store_files_in_db_view, name='store_files_in_db'),
    path('update-file-tree/', views.update_file_tree_view, name='update_file_tree'),
    path('update-file-or-files/', views.update_file_or_files_view, name='update_file_or_files'),
    path('get-file-or-files/', views.get_file_or_files_view, name='get_file_or_files'),
    path('delete-file-or-files/', views.delete_file_or_files_view, name='delete_file_or_files'),
    path('get-current-tree/', views.get_current_tree_view, name='get_current_tree'),
    path('get-updated-tree/', views.get_updated_tree_view, name='get_updated_tree'),
]
