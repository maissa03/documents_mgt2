from django.urls import path
from .views import user_login, user_logout
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]
