from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import HttpResponse

from apps.catalog.selectors.category import CategorySelector
from apps.catalog.selectors.product import ProductSelector
from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem, Transaction
from apps.orders.services.order import (
    create_order,
    add_or_update_item_in_order,
    remove_item_from_order,
    recalculate_total,
)
from apps.orders.services.payment import register_transaction, TransactionError
from apps.orders.services.payment_calculator import (
    calculate_iva_breakdown,
    calculate_suggested_tip,
    PaymentCalculatorError,
)
from apps.orders.selectors.transaction import TransactionSelector
from apps.orders.selectors.order_item import OrderItemSelector
from apps.orders.models import PaymentMethod
from apps.dining.models import DiningTable
from apps.dining.services.table import DiningTableService, DiningTableError
from apps.core.constants.actions import SystemActions


def _get_or_create_order_for_session(request):
    order_id = request.session.get('order_id')
    order = None
    if order_id:
        try:
            order = Order.objects.for_tenant(request.tenant).get(id=order_id, estado__in=Order.ACTIVE_STATES)
        except Order.DoesNotExist:
            order = None
    if not order:
        order = create_order(user=request.user, tenant=request.tenant, tipo_flujo=Order.Flow.RAPIDO)
        request.session['order_id'] = order.id
    return order


def _build_payment_context(order, tenant, table=None):
    """Construye el contexto común para vistas de pago.

    Incluye desglose de consumo, propinas pagadas y sugerencias.
    """
    iva_breakdown = calculate_iva_breakdown(order, tenant)
    suggested_tip = TransactionSelector.suggested_tip(order)
    total_consumo_paid = TransactionSelector.total_consumo_paid(order)
    total_tip_paid = TransactionSelector.total_tip_paid(order)
    total_consumo = TransactionSelector.total_cuenta(order)
    total_pending = TransactionSelector.total_pending(order)
    suggested_tip_pending = TransactionSelector.suggested_tip_pending(order)
    total_pending_with_tip = TransactionSelector.total_pending_with_tip(order)
    total_pagado = total_consumo_paid + total_tip_paid
    unpaid_items = OrderItemSelector.get_unpaid_items(order)
    paid_items = OrderItemSelector.get_paid_items(order)
    transactions = TransactionSelector.list_for_order(order).select_related('order', 'payment_method')
    payment_methods = PaymentMethod.objects.for_tenant(tenant).filter(activo=True)

    return {
        'order': order,
        'table': table,
        'iva_breakdown': iva_breakdown,
        'suggested_tip': suggested_tip,
        'total_consumo_paid': total_consumo_paid,
        'total_tip_paid': total_tip_paid,
        'total_consumo': total_consumo,
        'total_pending': total_pending,
        'suggested_tip_pending': suggested_tip_pending,
        'total_pending_with_tip': total_pending_with_tip,
        'total_pagado': total_pagado,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
        'transactions': transactions,
        'payment_methods': payment_methods,
    }


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
    
    order_items = order.items.exclude(estado='ANULADO').select_related('product')
    ctx = _build_payment_context(order, request.tenant, table=table)
    ctx['order_items'] = order_items
    ctx['products'] = products
    ctx['categories'] = categories
    ctx['has_active_items'] = order_items.exists()
    
    return render(request, 'orders/mesa_pedido.html', ctx)


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
    
    # After confirming order, redirect to mesa view
    response = HttpResponse(status=200)
    response['HX-Redirect'] = '/ordenes/mesa/' + str(table_id) + '/'
    return response


@login_required
def mesa_solicitar_cuenta(request, table_id):
    """Transiciona mesa de OCUPADA a PAGANDO y retorna partials actualizados."""
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=table_id)
    order = get_object_or_404(Order.objects.for_tenant(request.tenant), table=table, estado__in=Order.ACTIVE_STATES)

    try:
        DiningTableService.set_table_paying(user=request.user, table=table)
    except DiningTableError as e:
        return HttpResponse(str(e), status=400)

    order_items = order.items.exclude(estado='ANULADO').select_related('product')
    ctx = _build_payment_context(order, request.tenant, table=table)
    ctx['order_items'] = order_items
    ctx['has_active_items'] = order_items.exists()

    cuenta_html = render(request, 'orders/partials/cuenta_actualizada.html', ctx).content.decode()

    actions_html = render(request, 'orders/partials/mesa_actions.html', {
        'order': order,
        'table': table,
        'has_active_items': order_items.exists(),
    }).content.decode()

    # Return both partials; HTMX will swap target and process OOB
    response = HttpResponse(cuenta_html + actions_html)
    response['HX-Trigger'] = 'mesaStateUpdated'
    return response


@login_required
def mesa_liberar_mesa(request, table_id):
    """Libera una mesa OCUPADA o PAGANDO sin movimientos activos."""
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=table_id)

    try:
        DiningTableService.release_table(user=request.user, table=table)
    except DiningTableError as e:
        return HttpResponse(str(e), status=400)

    response = HttpResponse(status=200)
    response['HX-Redirect'] = '/salon/mesas/'
    return response


@login_required
def mesa_modal_pago(request, table_id):
    """Retorna el modal de pago con desglose completo para una mesa."""
    table = get_object_or_404(DiningTable.objects.for_tenant(request.tenant), pk=table_id)
    order = get_object_or_404(Order.objects.for_tenant(request.tenant), table=table, estado__in=Order.ACTIVE_STATES)

    ctx = _build_payment_context(order, request.tenant, table=table)
    return render(request, 'orders/partials/modal_pago.html', ctx)


@login_required
def orden_procesar_pago(request, order_id):
    """Procesa un pago y retorna resultado (modal actualizado o redirección)."""
    order = get_object_or_404(Order.objects.for_tenant(request.tenant), pk=order_id)

    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)

    tipo_pago = request.POST.get('tipo_pago')
    monto = request.POST.get('monto')
    items_ids = request.POST.getlist('items[]')
    cantidades_vals = request.POST.getlist('cantidades[]')
    payment_method_id = request.POST.get('payment_method')
    tip_amount = request.POST.get('tip_amount', '0')

    payment_method = None
    if payment_method_id:
        payment_method = get_object_or_404(PaymentMethod.objects.for_tenant(request.tenant), pk=payment_method_id)

    order_items = None
    cantidades = None
    if tipo_pago == Transaction.PaymentType.PRODUCTOS and items_ids:
        order_items = list(OrderItem.objects.for_tenant(request.tenant).filter(pk__in=items_ids, order=order))
        if cantidades_vals and len(cantidades_vals) == len(items_ids):
            cantidades = {items_ids[i]: int(cantidades_vals[i]) for i in range(len(items_ids))}

    try:
        transaction_record = register_transaction(
            user=request.user,
            tenant=request.tenant,
            order=order,
            payment_type=tipo_pago,
            amount=monto if monto else None,
            order_items=order_items,
            cantidades=cantidades,
            payment_method=payment_method,
            tip_amount=Decimal(tip_amount) if tip_amount else Decimal('0'),
        )
    except (TransactionError, PaymentCalculatorError) as e:
        order.refresh_from_db()
        table = order.table if order.table_id else None
        ctx = _build_payment_context(order, request.tenant, table=table)
        ctx['error'] = str(e)
        template = 'orders/partials/modal_pago.html' if order.table_id else 'orders/partials/terminal_modal_pago.html'
        return render(request, template, ctx, status=400)

    order.refresh_from_db()

    if order.estado == Order.States.COMPLETADO:
        if order.table_id:
            response = HttpResponse(status=200)
            response['HX-Redirect'] = '/salon/mesas/'
            return response
        else:
            # Rapid flow - redirect to terminal to reset cart
            response = HttpResponse(status=200)
            response['HX-Redirect'] = '/ordenes/terminal-ventas/'
            return response

    if order.estado == Order.States.CONFIRMADO and not order.table_id:
        # Rapid flow confirmed but not completed (may still have pending tip or additional payments)
        # Return updated modal so user can continue operating
        table = order.table if order.table_id else None
        ctx = _build_payment_context(order, request.tenant, table=table)
        ctx['success'] = 'Pago registrado exitosamente'
        return render(request, 'orders/partials/terminal_modal_pago.html', ctx)

    table = order.table if order.table_id else None
    ctx = _build_payment_context(order, request.tenant, table=table)
    ctx['success'] = 'Pago registrado exitosamente'
    template = 'orders/partials/modal_pago.html' if order.table_id else 'orders/partials/terminal_modal_pago.html'
    return render(request, template, ctx)


@login_required
def orden_pre_cuenta(request, order_id):
    """Retorna la pre-cuenta detallada con items pagados y no pagados."""
    order = get_object_or_404(Order.objects.for_tenant(request.tenant), pk=order_id)

    ctx = _build_payment_context(order, request.tenant)
    return render(request, 'orders/partials/pre_cuenta.html', ctx)


@login_required
def terminal_modal_pago(request):
    """Retorna el modal de pago para flujo rápido (terminal de ventas)."""
    order_id = request.session.get('order_id')
    if not order_id:
        return HttpResponse('No hay orden activa', status=400)

    order = get_object_or_404(Order.objects.for_tenant(request.tenant), pk=order_id, estado__in=Order.ACTIVE_STATES)

    ctx = _build_payment_context(order, request.tenant)
    return render(request, 'orders/partials/terminal_modal_pago.html', ctx)
