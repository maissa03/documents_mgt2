'''from django.urls import path
from .views import user_login, user_logout
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    
]'''

from django.contrib import admin
from django.urls import include, path
from users import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', accounts_views.register, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    

    path('admin-page/',accounts_views.admin_view, name='admin_view')

]
