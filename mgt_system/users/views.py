from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import JsonResponse

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
    return JsonResponse({'message': 'You have access!'})





