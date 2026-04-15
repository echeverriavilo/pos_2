from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods


def home(request):
    return render(request, 'core/home.html')


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña inválidos.')
            return render(request, 'core/login.html')
    else:
        return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def config(request):
    return render(request, 'core/config.html')