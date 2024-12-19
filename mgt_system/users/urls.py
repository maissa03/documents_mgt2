'''from django.urls import path
from .views import user_login, user_logout
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    
]'''
"""
from django.contrib import admin
from django.urls import include, path
from users import views as accounts_views
from .views import register, login_view, admin_view, manager_dashboard, employee_dashboard
urlpatterns = [
    path('admin/', admin.site.urls),
     path('register/', accounts_views.register, name='register'),
        path('login/', accounts_views.login_view, name='login'),
        
        path('admin-page/', accounts_views.admin_view, name='admin_view'),
        path('manager-dashboard/', accounts_views.manager_dashboard, name='manager_dashboard'),
        path('employee-dashboard/', accounts_views.employee_dashboard, name='employee_dashboard'),

]
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    admin_view,
    manager_dashboard,
    employee_dashboard,
    UserViewSet,
)
from django.views.generic import TemplateView

# Initialize Router for the UserViewSet
"""
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
"""

urlpatterns = [
    # Admin Site
    path('admin/', admin.site.urls),

    # API Endpoints
    path('users/api/register/', RegisterView.as_view(), name='api-register'),
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('users/api/admin-page/', admin_view, name='api-admin-view'),
    path('users/api/manager-dashboard/', manager_dashboard, name='api-manager-dashboard'),
    path('users/api/employee-dashboard/', employee_dashboard, name='api-employee-dashboard'),
    #path('users/api/', include(router.urls)),

    # HTML Pages (Template-Based Views)
    path('', TemplateView.as_view(template_name='users/index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='users/login.html'), name='login-page'),
    path('register/', TemplateView.as_view(template_name='users/register.html'), name='register-page'),
    path('dashboard/admin/', TemplateView.as_view(template_name='users/admin_page.html'), name='admin-dashboard'),
    path('dashboard/manager/', TemplateView.as_view(template_name='users/manager_dashboard.html'), name='manager-dashboard'),
    path('dashboard/employee/', TemplateView.as_view(template_name='users/employee_dashboard.html'), name='employee-dashboard'),
    
]

