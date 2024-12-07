"""from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse

from rest_framework import viewsets
from .models import CustomUser
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return render(request, 'users/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse

@login_required
@permission_required('users.add_document', raise_exception=True)
def restricted_view(request):
    return JsonResponse({'message': 'You have access!'})"""

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.contrib.auth.models import Group, User
from .serializers import UserSerializer
from rest_framework import viewsets

# Register view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
             # Add the user to the 'Employees' group by default
            employees_group = Group.objects.get(name='Employee')
            user.groups.add(employees_group)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect based on role
            if user.groups.filter(name='Administrator').exists():
                print("User is an Administrator.")
                return redirect('admin_view')
            elif user.groups.filter(name='Employee').exists():
                return redirect('employee_dashboard')  # Redirect to document list or creation form
            elif user.groups.filter(name='Manager').exists():
                return redirect('manager_dashboard')  # Redirect to document list or creation form
            else:
                return HttpResponseForbidden("You do not have permission to access this page.")
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

# Group-required decorator
def group_required(group_name):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not request.user.groups.filter(name=group_name).exists():
                return HttpResponseForbidden("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Admin-only view
@login_required
@group_required('Administrator')
def admin_view(request):
    return render(request, 'users/admin_page.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden

# Function to check if user is a manager
def is_manager(user):
    return user.groups.filter(name='Manager').exists()

# Function to check if user is an employee
def is_employee(user):
    return user.groups.filter(name='Employee').exists()

@login_required
@user_passes_test(is_manager, login_url='login')
def manager_dashboard(request):
    return render(request, 'users/manager_dashboard.html')

@login_required
@user_passes_test(is_employee, login_url='login')
def employee_dashboard(request):
    return render(request, 'users/employee_dashboard.html')



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


