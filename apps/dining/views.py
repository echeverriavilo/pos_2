from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def table_map(request):
    return render(request, 'dining/table_map.html')