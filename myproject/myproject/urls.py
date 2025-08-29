from django.contrib import admin
from django.urls import path
from auth_system import views as auth_views
from business_app import views as business_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Аутентификация
    path('api/register/', auth_views.register),
    path('api/login/', auth_views.login),
    path('api/logout/', auth_views.logout),
    path('api/profile/', auth_views.profile),
    path('api/delete-account/', auth_views.delete_account),

    # Администрирование (только для админов)
    path('api/admin/roles/', auth_views.role_list),

    # Бизнес-объекты
    path('api/products/', business_views.products_list),
    path('api/products/create/', business_views.create_product),
]
