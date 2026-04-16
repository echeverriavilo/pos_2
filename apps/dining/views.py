from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from apps.core.models import CustomUser
from apps.dining.models import DiningTable
from apps.dining.selectors.table import DiningTableSelector
from apps.dining.services.table import DiningTableService, DiningTableError


@login_required
def table_map(request):
    tables = DiningTableSelector.list_for_tenant(request.tenant)
    return render(request, 'dining/table_map.html', {'tables': tables})


@login_required
def table_open_modal(request, pk):
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=pk)
    waiters = CustomUser.objects.filter(membership__tenant=request.tenant, is_active=True)
    return render(request, 'dining/partials/open_modal.html', {'table': table, 'waiters': waiters})


@login_required
def table_open(request, pk):
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=pk)
    try:
        order = DiningTableService.open_table(user=request.user, table=table)
        request.session['order_id'] = order.id
        
        response = HttpResponse(status=204)
        response['HX-Redirect'] = reverse('orders:mesa-pedido', kwargs={'table_id': table.id})
        return response
    except DiningTableError as e:
        return HttpResponse(str(e), status=400)


@login_required
def table_redirect(request, pk):
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=pk)
    order = DiningTableSelector.get_active_order_for_table(table)
    
    if order:
        request.session['order_id'] = order.id
        response = HttpResponse(status=204)
        response['HX-Redirect'] = reverse('orders:mesa-pedido', kwargs={'table_id': table.id})
        return response
        
    return HttpResponse("No hay orden activa para esta mesa", status=404)