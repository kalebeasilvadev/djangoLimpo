from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {"name":"index"})

def corpo(request):
    return render(request, 'corpo.html', {})

def login(request):
    return render(request, 'pages/login/login.html', {})

def config(request):
    return render(request, 'pages/config/config.html', {})

def menu(request):
    return render(request, 'pages/menu/menu.html', {})

def usuario(request):
    return render(request, 'pages/usuario/usuario.html', {})

def dashboard(request):
    return render(request, 'pages/dashboard/dashboard.html', {})