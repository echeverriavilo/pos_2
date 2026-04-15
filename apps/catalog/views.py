from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def product_list(request):
    return render(request, 'catalog/product_list.html')


@login_required
def category_list(request):
    return render(request, 'catalog/category_list.html')