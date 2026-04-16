from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.catalog.selectors.category import CategorySelector
from apps.catalog.selectors.product import ProductSelector
from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem
from apps.orders.services.order import (
    create_order,
    add_or_update_item_in_order,
    remove_item_from_order,
    recalculate_total,
)
from apps.core.constants.actions import SystemActions
from django.http import HttpResponse


def _get_or_create_order_for_session(request):
    order_id = request.session.get('order_id')
    order = None
    if order_id:
        try:
            order = Order.objects.for_tenant(request.tenant).get(id=order_id, estado=Order.States.ABIERTO)
        except Order.DoesNotExist:
            order = None
    if not order:
        order = create_order(user=request.user, tenant=request.tenant, tipo_flujo=Order.Flow.RAPIDO)
        request.session['order_id'] = order.id
    return order


class TerminalVentasView(LoginRequiredMixin, TemplateView):
    template_name = "orders/terminal_ventas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorySelector.get_active_categories(self.request.tenant)
        context['current_order'] = _get_or_create_order_for_session(self.request)
        return context


@login_required
def product_list_partial(request):
    category_id = request.GET.get('category')
    search_term = request.GET.get('search')

    products = ProductSelector.search_active_products(
        tenant=request.tenant,
        category_id=category_id,
        search_term=search_term
    )
    return render(request, 'orders/partials/product_grid.html', {'products': products})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product.objects.for_tenant(request.tenant), id=product_id)
    order = _get_or_create_order_for_session(request)
    add_or_update_item_in_order(user=request.user, order=order, product=product, cantidad=1)
    recalculate_total(order)
    return render(request, 'orders/partials/shopping_cart.html', {'current_order': order})


@login_required
def remove_from_cart(request, order_item_id):
    order_item = get_object_or_404(OrderItem.objects.for_tenant(request.tenant), id=order_item_id)
    order = order_item.order
    remove_item_from_order(user=request.user, item=order_item)
    recalculate_total(order)
    return render(request, 'orders/partials/shopping_cart.html', {'current_order': order})


@login_required
def active_order(request):
    return render(request, 'orders/active_order.html')


@login_required
def new_order(request):
    return render(request, 'orders/new_order.html')


@login_required
def history(request):
    return render(request, 'orders/history.html')


@login_required
def mesa_pedido(request, table_id):
    from apps.dining.models import DiningTable
    from apps.dining.selectors import DiningTableSelector
    
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=table_id)
    order = DiningTableSelector.get_active_order_for_table(table)
    
    if not order:
        from django.contrib import messages
        messages.error(request, 'No hay orden activa para esta mesa.')
        from django.shortcuts import redirect
        return redirect('dining:table-map')
    
    products = ProductSelector.search_active_products(request.tenant)[:30]
    categories = CategorySelector.get_active_categories(request.tenant)
    
    return render(request, 'orders/mesa_pedido.html', {
        'table': table,
        'order': order,
        'order_items': order.items.exclude(estado='ANULADO').select_related('product'),
        'products': products,
        'categories': categories,
    })


@login_required
def mesa_nuevo_pedido_modal(request, table_id):
    from apps.dining.models import DiningTable
    from apps.dining.selectors import DiningTableSelector
    
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=table_id)
    order = DiningTableSelector.get_active_order_for_table(table)
    
    if not order:
        return HttpResponse('No hay orden activa', status=400)
    
    categories = CategorySelector.get_active_categories(request.tenant)
    products = ProductSelector.search_active_products(request.tenant)[:12]
    
    return render(request, 'orders/partials/nuevo_pedido_modal.html', {
        'table': table,
        'order': order,
        'categories': categories,
        'products': products,
    })


@login_required
def mesa_confirmar_pedido(request, table_id):
    import json
    from apps.dining.models import DiningTable
    from apps.dining.selectors import DiningTableSelector
    from apps.dining.services.table import DiningTableService
    from apps.catalog.models import Product
    from django.db import transaction
    
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=table_id)
    order = DiningTableSelector.get_active_order_for_table(table)
    
    if not order:
        return HttpResponse('No hay orden activa', status=400)
    
    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)
    
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
    except json.JSONDecodeError:
        return HttpResponse('Datos inválidos', status=400)
    
    if not items:
        return HttpResponse('No hay productos en el pedido', status=400)
    
    with transaction.atomic():
        for item in items:
            product_id = item.get('product_id')
            cantidad = item.get('cantidad', 1)
            
            product = get_object_or_404(Product.objects.for_tenant(request.tenant), pk=product_id)
            add_or_update_item_in_order(
                user=request.user,
                order=order,
                product=product,
                cantidad=cantidad
            )
        
        recalculate_total(order)
        
        if table.estado == DiningTable.States.PAGANDO:
            table = DiningTableService.reopen_table(user=request.user, table=table)
    
    return render(request, 'orders/partials/cuenta_actualizada.html', {
        'order': order,
        'order_items': order.items.exclude(estado='ANULADO').select_related('product'),
    })
