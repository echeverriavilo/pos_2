from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def active_order(request):
    return render(request, 'orders/active_order.html')


@login_required
def new_order(request):
    return render(request, 'orders/new_order.html')


@login_required
def history(request):
    return render(request, 'orders/history.html')