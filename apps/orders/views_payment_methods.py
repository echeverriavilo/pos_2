from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.orders.forms import PaymentMethodForm
from apps.orders.models import PaymentMethod
from apps.orders.services.payment_method import (
    PaymentMethodService,
    PaymentMethodServiceError,
)
from apps.core.services.auth import require_permission


@login_required
def payment_method_list(request):
    """Lista los métodos de pago del tenant."""
    require_permission(request.user, 'manage_cash_registers')
    payment_methods = PaymentMethod.objects.for_tenant(request.tenant).filter(
        inhabilitado=False,
    ).order_by('-activo', 'orden', 'nombre')
    return render(request, 'orders/payment_method_list.html', {
        'payment_methods': payment_methods,
    })


@login_required
def payment_method_create(request):
    """Crea un nuevo método de pago para el tenant."""
    require_permission(request.user, 'manage_cash_registers')
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            try:
                PaymentMethodService.create_payment_method(
                    tenant=request.tenant,
                    nombre=form.cleaned_data['nombre'],
                    orden=form.cleaned_data['orden'],
                )
                messages.success(request, 'Método de pago creado exitosamente.')
                return redirect('orders:payment-method-list')
            except PaymentMethodServiceError as e:
                form.add_error(None, str(e))
    else:
        form = PaymentMethodForm()
    return render(request, 'orders/payment_method_form.html', {
        'form': form,
        'title': 'Crear Método de Pago',
    })


@login_required
def payment_method_edit(request, pk):
    """Edita un método de pago existente del tenant."""
    require_permission(request.user, 'manage_cash_registers')
    payment_method = get_object_or_404(
        PaymentMethod.objects.for_tenant(request.tenant).filter(inhabilitado=False), pk=pk,
    )
    if request.method == 'POST':
        form = PaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            try:
                PaymentMethodService.update_payment_method(
                    payment_method=payment_method,
                    nombre=form.cleaned_data['nombre'],
                    orden=form.cleaned_data['orden'],
                )
                messages.success(request, 'Método de pago actualizado exitosamente.')
                return redirect('orders:payment-method-list')
            except PaymentMethodServiceError as e:
                form.add_error(None, str(e))
    else:
        form = PaymentMethodForm(instance=payment_method)
    return render(request, 'orders/payment_method_form.html', {
        'form': form,
        'title': 'Editar Método de Pago',
    })


@login_required
def payment_method_toggle(request, pk):
    """Pausa o reanuda un método de pago (desactivación temporal)."""
    require_permission(request.user, 'manage_cash_registers')
    payment_method = get_object_or_404(
        PaymentMethod.objects.for_tenant(request.tenant).filter(inhabilitado=False), pk=pk,
    )
    if request.method != 'POST':
        return redirect('orders:payment-method-list')
    PaymentMethodService.toggle_active(payment_method=payment_method)
    estado = "pausado" if not payment_method.activo else "reactivado"
    messages.success(request, f'Método de pago {estado}.')
    return redirect('orders:payment-method-list')


@login_required
def payment_method_inhabilitar(request, pk):
    """Inhabilita permanentemente un método de pago (no se puede reactivar)."""
    require_permission(request.user, 'manage_cash_registers')
    payment_method = get_object_or_404(PaymentMethod.objects.for_tenant(request.tenant), pk=pk)
    if request.method != 'POST':
        return redirect('orders:payment-method-list')
    payment_method.inhabilitado = True
    payment_method.activo = False
    payment_method.save(update_fields=['inhabilitado', 'activo'])
    messages.success(request, 'Método de pago inhabilitado permanentemente.')
    return redirect('orders:payment-method-list')
