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
    set_tip,
    PaymentCalculatorError,
)
from apps.orders.selectors.transaction import TransactionSelector
from apps.orders.selectors.order_item import OrderItemSelector
from apps.dining.models import DiningTable
from apps.dining.services.table import DiningTableService, DiningTableError
from apps.core.constants.actions import SystemActions


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
    
    order_items = order.items.exclude(estado='ANULADO').select_related('product')

    if order.propina_monto == Decimal('0'):
        suggested = calculate_suggested_tip(order)
        set_tip(user=request.user, order=order, amount=suggested)
        order.refresh_from_db()

    iva_breakdown = calculate_iva_breakdown(order, request.tenant)
    suggested_tip = calculate_suggested_tip(order)
    total_paid = TransactionSelector.total_paid(order)
    total_cuenta = TransactionSelector.total_cuenta(order)
    total_pending = TransactionSelector.total_pending(order)
    unpaid_items = OrderItemSelector.get_unpaid_items(order)
    paid_items = OrderItemSelector.get_paid_items(order)
    transactions = TransactionSelector.list_for_order(order).select_related('order')
    
    return render(request, 'orders/mesa_pedido.html', {
        'table': table,
        'order': order,
        'order_items': order_items,
        'products': products,
        'categories': categories,
        'has_active_items': order_items.exists(),
        'iva_breakdown': iva_breakdown,
        'suggested_tip': suggested_tip,
        'total_paid': total_paid,
        'total_cuenta': total_cuenta,
        'total_pending': total_pending,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
        'transactions': transactions,
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

    if order.propina_monto == Decimal('0'):
        suggested = calculate_suggested_tip(order)
        set_tip(user=request.user, order=order, amount=suggested)
        order.refresh_from_db()

    order_items = order.items.exclude(estado='ANULADO').select_related('product')
    iva_breakdown = calculate_iva_breakdown(order, request.tenant)
    suggested_tip = calculate_suggested_tip(order)
    total_paid = TransactionSelector.total_paid(order)
    total_cuenta = TransactionSelector.total_cuenta(order)
    total_pending = TransactionSelector.total_pending(order)
    unpaid_items = OrderItemSelector.get_unpaid_items(order)
    paid_items = OrderItemSelector.get_paid_items(order)
    transactions = TransactionSelector.list_for_order(order).select_related('order')

    cuenta_html = render(request, 'orders/partials/cuenta_actualizada.html', {
        'order': order,
        'order_items': order_items,
        'table': table,
        'iva_breakdown': iva_breakdown,
        'suggested_tip': suggested_tip,
        'total_paid': total_paid,
        'total_cuenta': total_cuenta,
        'total_pending': total_pending,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
        'transactions': transactions,
    }).content.decode()

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

    if order.propina_monto == Decimal('0'):
        suggested = calculate_suggested_tip(order)
        set_tip(user=request.user, order=order, amount=suggested)
        order.refresh_from_db()

    iva_breakdown = calculate_iva_breakdown(order, request.tenant)
    suggested_tip = calculate_suggested_tip(order)
    total_paid = TransactionSelector.total_paid(order)
    total_cuenta = TransactionSelector.total_cuenta(order)
    total_pending = TransactionSelector.total_pending(order)
    transactions = TransactionSelector.list_for_order(order).select_related('order')
    unpaid_items = OrderItemSelector.get_unpaid_items(order)
    paid_items = OrderItemSelector.get_paid_items(order)

    return render(request, 'orders/partials/modal_pago.html', {
        'order': order,
        'table': table,
        'iva_breakdown': iva_breakdown,
        'suggested_tip': suggested_tip,
        'total_paid': total_paid,
        'total_cuenta': total_cuenta,
        'total_pending': total_pending,
        'transactions': transactions,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
    })


@login_required
def orden_fijar_propina(request, order_id):
    """Establece el monto de propina en una orden y retorna modal de pago actualizado."""
    from apps.orders.selectors.order_item import OrderItemSelector

    order = get_object_or_404(Order.objects.for_tenant(request.tenant), pk=order_id)

    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)

    try:
        propina_monto = Decimal(request.POST.get('propina_monto', '0'))
    except Exception:
        return HttpResponse('Monto de propina inválido', status=400)

    try:
        set_tip(user=request.user, order=order, amount=propina_monto)
    except PaymentCalculatorError as e:
        return HttpResponse(str(e), status=400)

    order.refresh_from_db()
    iva_breakdown = calculate_iva_breakdown(order, request.tenant)
    suggested_tip = calculate_suggested_tip(order)
    total_paid = TransactionSelector.total_paid(order)
    total_cuenta = TransactionSelector.total_cuenta(order)
    total_pending = TransactionSelector.total_pending(order)
    transactions = TransactionSelector.list_for_order(order).select_related('order')
    unpaid_items = OrderItemSelector.get_unpaid_items(order)
    paid_items = OrderItemSelector.get_paid_items(order)

    table = None
    if order.table_id:
        table = order.table

    template = 'orders/partials/modal_pago.html' if order.table_id else 'orders/partials/terminal_modal_pago.html'

    return render(request, template, {
        'order': order,
        'table': table,
        'iva_breakdown': iva_breakdown,
        'suggested_tip': suggested_tip,
        'total_paid': total_paid,
        'total_cuenta': total_cuenta,
        'total_pending': total_pending,
        'transactions': transactions,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
        'success': 'Propina actualizada',
    })


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
        )
    except (TransactionError, PaymentCalculatorError) as e:
        order.refresh_from_db()
        iva_breakdown = calculate_iva_breakdown(order, request.tenant)
        suggested_tip = calculate_suggested_tip(order)
        total_paid = TransactionSelector.total_paid(order)
        total_cuenta = TransactionSelector.total_cuenta(order)
        total_pending = TransactionSelector.total_pending(order)
        transactions = TransactionSelector.list_for_order(order)
        unpaid_items = OrderItemSelector.get_unpaid_items(order)
        paid_items = OrderItemSelector.get_paid_items(order)

        table = order.table if order.table_id else None
        template = 'orders/partials/modal_pago.html' if order.table_id else 'orders/partials/terminal_modal_pago.html'
        return render(request, template, {
            'order': order,
            'table': table,
            'iva_breakdown': iva_breakdown,
            'suggested_tip': suggested_tip,
            'total_paid': total_paid,
            'total_cuenta': total_cuenta,
            'total_pending': total_pending,
            'transactions': transactions,
            'unpaid_items': unpaid_items,
            'paid_items': paid_items,
            'error': str(e),
        }, status=400)

    order.refresh_from_db()

    if order.estado in {Order.States.COMPLETADO, Order.States.CONFIRMADO}:
        if order.table_id:
            response = HttpResponse(status=200)
            response['HX-Redirect'] = '/salon/mesas/'
            return response
        else:
            # Rapid flow - redirect to terminal to reset cart
            response = HttpResponse(status=200)
            response['HX-Redirect'] = '/ordenes/terminal-ventas/'
            return response

    iva_breakdown = calculate_iva_breakdown(order, request.tenant)
    suggested_tip = calculate_suggested_tip(order)
    total_paid = TransactionSelector.total_paid(order)
    total_cuenta = TransactionSelector.total_cuenta(order)
    total_pending = TransactionSelector.total_pending(order)
    transactions = TransactionSelector.list_for_order(order)
    unpaid_items = OrderItemSelector.get_unpaid_items(order)
    paid_items = OrderItemSelector.get_paid_items(order)

    table = order.table if order.table_id else None
    template = 'orders/partials/modal_pago.html' if order.table_id else 'orders/partials/terminal_modal_pago.html'
    return render(request, template, {
        'order': order,
        'table': table,
        'iva_breakdown': iva_breakdown,
        'suggested_tip': suggested_tip,
        'total_paid': total_paid,
        'total_cuenta': total_cuenta,
        'total_pending': total_pending,
        'transactions': transactions,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
        'success': 'Pago registrado exitosamente',
    })


@login_required
def orden_pre_cuenta(request, order_id):
    """Retorna la pre-cuenta detallada con items pagados y no pagados."""
    order = get_object_or_404(Order.objects.for_tenant(request.tenant), pk=order_id)

    iva_breakdown = calculate_iva_breakdown(order, request.tenant)
    suggested_tip = calculate_suggested_tip(order)
    total_paid = TransactionSelector.total_paid(order)
    total_cuenta = TransactionSelector.total_cuenta(order)
    total_pending = TransactionSelector.total_pending(order)
    transactions = TransactionSelector.list_for_order(order)
    unpaid_items = OrderItemSelector.get_unpaid_items(order)
    paid_items = OrderItemSelector.get_paid_items(order)

    return render(request, 'orders/partials/pre_cuenta.html', {
        'order': order,
        'iva_breakdown': iva_breakdown,
        'suggested_tip': suggested_tip,
        'total_paid': total_paid,
        'total_cuenta': total_cuenta,
        'total_pending': total_pending,
        'transactions': transactions,
        'unpaid_items': unpaid_items,
        'paid_items': paid_items,
    })


@login_required
def terminal_modal_pago(request):
    """Retorna el modal de pago para flujo rápido (terminal de ventas)."""
    order_id = request.session.get('order_id')
    if not order_id:
        return HttpResponse('No hay orden activa', status=400)

    order = get_object_or_404(Order.objects.for_tenant(request.tenant), pk=order_id, estado__in=Order.ACTIVE_STATES)

    if order.propina_monto == Decimal('0'):
        suggested = calculate_suggested_tip(order)
        set_tip(user=request.user, order=order, amount=suggested)
        order.refresh_from_db()

    iva_breakdown = calculate_iva_breakdown(order, request.tenant)
    suggested_tip = calculate_suggested_tip(order)
    total_paid = TransactionSelector.total_paid(order)
    total_cuenta = TransactionSelector.total_cuenta(order)
    total_pending = TransactionSelector.total_pending(order)
    transactions = TransactionSelector.list_for_order(order)

    return render(request, 'orders/partials/terminal_modal_pago.html', {
        'order': order,
        'iva_breakdown': iva_breakdown,
        'suggested_tip': suggested_tip,
        'total_paid': total_paid,
        'total_cuenta': total_cuenta,
        'total_pending': total_pending,
        'transactions': transactions,
    })
