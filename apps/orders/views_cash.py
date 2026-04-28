from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from apps.orders.models import CashCloseDetail, CashRegister, CashSession, PaymentMethod
from apps.orders.selectors.cash_register import CashRegisterSelector
from apps.orders.selectors.cash_session import CashSessionSelector
from apps.orders.services.cash_register import (
    create_cash_register,
    update_cash_register,
    toggle_cash_register,
    CashRegisterError,
)
from apps.orders.services.cash_session import (
    open_cash_session,
    close_cash_session,
    register_cash_movement,
    get_session_summary,
    CashSessionError,
    CashMovementError,
)


@login_required
def caja_lista(request):
    """Lista las cajas del tenant y sus sesiones activas."""
    cash_registers = CashRegisterSelector.list_cash_registers(request.tenant)
    active_sessions = {}
    for cr in cash_registers:
        session = CashSessionSelector.get_active_session_for_register(request.tenant, cr)
        if session:
            active_sessions[cr.pk] = session

    return render(request, 'orders/cash_registers.html', {
        'cash_registers': cash_registers,
        'active_sessions': active_sessions,
    })


@login_required
def caja_crear(request):
    """Crea una nueva caja."""
    if request.method != 'POST':
        return redirect('orders:caja-lista')

    nombre = request.POST.get('nombre', '').strip()
    soporta_flujo_mesa = request.POST.get('soporta_flujo_mesa') == 'on'
    soporta_flujo_rapido = request.POST.get('soporta_flujo_rapido') == 'on'

    try:
        create_cash_register(
            user=request.user,
            tenant=request.tenant,
            nombre=nombre,
            soporta_flujo_mesa=soporta_flujo_mesa,
            soporta_flujo_rapido=soporta_flujo_rapido,
        )
    except CashRegisterError as e:
        cash_registers = CashRegisterSelector.list_cash_registers(request.tenant)
        return render(request, 'orders/cash_registers.html', {
            'cash_registers': cash_registers,
            'active_sessions': {},
            'error': str(e),
        })

    return redirect('orders:caja-lista')


@login_required
def caja_editar(request, pk):
    """Edita una caja existente."""
    cash_register = get_object_or_404(CashRegister.objects.for_tenant(request.tenant), pk=pk)

    if request.method != 'POST':
        return render(request, 'orders/cash_register_form.html', {
            'cash_register': cash_register,
        })

    nombre = request.POST.get('nombre', '').strip()
    soporta_flujo_mesa = request.POST.get('soporta_flujo_mesa') == 'on'
    soporta_flujo_rapido = request.POST.get('soporta_flujo_rapido') == 'on'

    try:
        update_cash_register(
            user=request.user,
            tenant=request.tenant,
            pk=pk,
            nombre=nombre,
            soporta_flujo_mesa=soporta_flujo_mesa,
            soporta_flujo_rapido=soporta_flujo_rapido,
        )
    except CashRegisterError as e:
        return render(request, 'orders/cash_register_form.html', {
            'cash_register': cash_register,
            'error': str(e),
        })

    return redirect('orders:caja-lista')


@login_required
def caja_toggle_activa(request, pk):
    """Activa o desactiva una caja."""
    if request.method != 'POST':
        return HttpResponse('Método no permitido', status=405)

    activo = request.POST.get('activo') == 'true'
    try:
        toggle_cash_register(user=request.user, tenant=request.tenant, pk=pk, activo=activo)
    except CashRegisterError as e:
        return HttpResponse(str(e), status=400)

    return redirect('orders:caja-lista')


@login_required
def sesion_abrir(request):
    """Abre una nueva sesión de caja."""
    if request.method != 'POST':
        cash_registers = CashRegister.objects.for_tenant(request.tenant).filter(activo=True)
        return render(request, 'orders/cash_session_open.html', {
            'cash_registers': cash_registers,
        })

    cash_register_id = request.POST.get('cash_register_id')
    monto_apertura = request.POST.get('monto_apertura', '0')

    try:
        session = open_cash_session(
            user=request.user,
            tenant=request.tenant,
            cash_register_id=cash_register_id,
            monto_apertura=Decimal(monto_apertura),
        )
    except CashSessionError as e:
        cash_registers = CashRegister.objects.for_tenant(request.tenant).filter(activo=True)
        return render(request, 'orders/cash_session_open.html', {
            'cash_registers': cash_registers,
            'error': str(e),
        })

    return redirect('orders:sesion-detalle', session_id=session.pk)


@login_required
def sesion_detalle(request, session_id):
    """Muestra el detalle de una sesión de caja."""
    session = get_object_or_404(CashSession.objects.for_tenant(request.tenant), pk=session_id)
    movements = CashSessionSelector.list_session_movements(session)

    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro in {'INGRESO', 'EGRESO', 'AJUSTE'}:
        movements = movements.filter(tipo=tipo_filtro)

    summary = None
    close_details = None
    payment_methods = None
    if session.estado == CashSession.States.CERRADA:
        summary = get_session_summary(session)
        close_details = CashCloseDetail.objects.filter(cash_session=session)
    else:
        payment_methods = PaymentMethod.objects.for_tenant(request.tenant).filter(activo=True)

    return render(request, 'orders/cash_session_detail.html', {
        'session': session,
        'movements': movements,
        'summary': summary,
        'close_details': close_details,
        'payment_methods': payment_methods,
    })


@login_required
def sesion_cerrar(request, session_id):
    """Cierra una sesión de caja con cuadratura por medio de pago."""
    session = get_object_or_404(CashSession.objects.for_tenant(request.tenant), pk=session_id)

    payment_methods = PaymentMethod.objects.for_tenant(request.tenant).filter(activo=True)

    if request.method != 'POST':
        if session.estado != CashSession.States.ABIERTA:
            return redirect('orders:sesion-detalle', session_id=session.pk)

        breakdown = CashSessionSelector.get_session_payment_breakdown(session)
        summary = get_session_summary(session)

        # Incluir monto_apertura en el breakdown de Efectivo para mostrarlo en pantalla
        efectivo_pm = PaymentMethod.objects.for_tenant(request.tenant).filter(
            nombre__iexact='Efectivo', activo=True,
        ).first()
        if efectivo_pm and session.monto_apertura > Decimal('0'):
            breakdown[efectivo_pm.pk] = breakdown.get(efectivo_pm.pk, Decimal('0')) + session.monto_apertura

        return render(request, 'orders/cash_session_close.html', {
            'session': session,
            'summary': summary,
            'payment_methods': payment_methods,
            'breakdown': breakdown,
        })

    comentario_cierre = request.POST.get('comentario_cierre', '')

    payment_details = []
    payment_declared = {}
    payment_comentarios = {}
    payment_diffs = {}
    for pm in payment_methods:
        val = request.POST.get(f'pm_declarado_{pm.pk}', '0')
        pm_comentario = request.POST.get(f'pm_comentario_{pm.pk}', '')
        payment_details.append({
            'payment_method_id': pm.pk,
            'monto_declarado': val,
            'comentario': pm_comentario,
        })
        payment_declared[pm.pk] = val
        payment_comentarios[pm.pk] = pm_comentario

    # Validar que al menos un medio de pago tenga monto declarado
    if not any(Decimal(d['monto_declarado']) != Decimal('0') for d in payment_details):
        summary = get_session_summary(session)
        breakdown = CashSessionSelector.get_session_payment_breakdown(session)
        efectivo_pm = PaymentMethod.objects.for_tenant(request.tenant).filter(
            nombre__iexact='Efectivo', activo=True,
        ).first()
        if efectivo_pm and session.monto_apertura > Decimal('0'):
            breakdown[efectivo_pm.pk] = breakdown.get(efectivo_pm.pk, Decimal('0')) + session.monto_apertura
        return render(request, 'orders/cash_session_close.html', {
            'session': session,
            'summary': summary,
            'payment_methods': payment_methods,
            'breakdown': breakdown,
            'error': 'Debe ingresar al menos un monto declarado para los medios de pago.',
        })

    # Calcular breakdown con apertura para mostrar en la confirmación
    breakdown = CashSessionSelector.get_session_payment_breakdown(session)
    efectivo_pm = PaymentMethod.objects.for_tenant(request.tenant).filter(
        nombre__iexact='Efectivo', activo=True,
    ).first()
    if efectivo_pm and session.monto_apertura > Decimal('0'):
        breakdown[efectivo_pm.pk] = breakdown.get(efectivo_pm.pk, Decimal('0')) + session.monto_apertura

    summary = get_session_summary(session)

    # Precalcular diferencias por medio de pago
    total_declarado = Decimal('0')
    for pm_id in payment_declared:
        sistema = breakdown.get(pm_id, Decimal('0'))
        declarado = Decimal(payment_declared.get(pm_id, '0'))
        payment_diffs[pm_id] = declarado - sistema
        total_declarado += declarado

    dif_general = total_declarado - summary['total_esperado']
    saldo_real = total_declarado

    return render(request, 'orders/cash_session_close_confirm.html', {
        'session': session,
        'summary': summary,
        'payment_methods': payment_methods,
        'breakdown': breakdown,
        'payment_declared': payment_declared,
        'payment_comentarios': payment_comentarios,
        'payment_diffs': payment_diffs,
        'total_declarado': total_declarado,
        'dif_general': dif_general,
        'saldo_real': saldo_real,
        'comentario_cierre': comentario_cierre,
    })


@login_required
def sesion_movimiento(request, session_id):
    """Registra un movimiento manual de caja."""
    session = get_object_or_404(CashSession.objects.for_tenant(request.tenant), pk=session_id)

    if request.method != 'POST':
        payment_methods = PaymentMethod.objects.for_tenant(request.tenant).filter(activo=True)
        return render(request, 'orders/partials/cash_movement_form.html', {
            'session': session,
            'payment_methods': payment_methods,
        })

    tipo = request.POST.get('tipo')
    monto = Decimal(request.POST.get('monto'))
    descripcion = request.POST.get('descripcion', '')
    payment_method_id = request.POST.get('payment_method_id') or None

    # AJUSTE: signo determina si es crédito (+) o débito (-)
    if tipo == 'AJUSTE' and request.POST.get('signo_ajuste') == 'negativo':
        monto = -monto

    try:
        register_cash_movement(
            user=request.user,
            tenant=request.tenant,
            session_id=session_id,
            tipo=tipo,
            monto=Decimal(monto),
            descripcion=descripcion,
            payment_method_id=payment_method_id,
        )
    except CashMovementError as e:
        payment_methods = PaymentMethod.objects.for_tenant(request.tenant).filter(activo=True)
        return render(request, 'orders/partials/cash_movement_form.html', {
            'session': session,
            'payment_methods': payment_methods,
            'error': str(e),
        })

    movements = CashSessionSelector.list_session_movements(session)
    payment_methods = PaymentMethod.objects.for_tenant(request.tenant).filter(activo=True)
    return render(request, 'orders/cash_session_detail.html', {
        'session': session,
        'movements': movements,
        'summary': None,
        'close_details': None,
        'payment_methods': payment_methods,
    })


@login_required
def sesion_confirmar(request, session_id):
    """Confirma el cierre de una sesión de caja con los datos ya revisados."""
    session = get_object_or_404(CashSession.objects.for_tenant(request.tenant), pk=session_id)

    if request.method != 'POST':
        return redirect('orders:sesion-cerrar', session_id=session_id)

    payment_methods = PaymentMethod.objects.for_tenant(request.tenant).filter(activo=True)

    comentario_cierre = request.POST.get('comentario_cierre', '')

    payment_details = []
    for pm in payment_methods:
        val = request.POST.get(f'pm_declarado_{pm.pk}', '0')
        pm_comentario = request.POST.get(f'pm_comentario_{pm.pk}', '')
        payment_details.append({
            'payment_method_id': pm.pk,
            'monto_declarado': val,
            'comentario': pm_comentario,
        })

    try:
        close_cash_session(
            user=request.user,
            tenant=request.tenant,
            session_id=session_id,
            payment_details=payment_details,
            comentario_cierre=comentario_cierre,
        )
    except CashSessionError as e:
        summary = get_session_summary(session)
        breakdown = CashSessionSelector.get_session_payment_breakdown(session)
        efectivo_pm = PaymentMethod.objects.for_tenant(request.tenant).filter(
            nombre__iexact='Efectivo', activo=True,
        ).first()
        if efectivo_pm and session.monto_apertura > Decimal('0'):
            breakdown[efectivo_pm.pk] = breakdown.get(efectivo_pm.pk, Decimal('0')) + session.monto_apertura

        payment_declared = {}
        payment_comentarios = {}
        payment_diffs = {}
        total_declarado = Decimal('0')
        for pm in payment_methods:
            payment_declared[pm.pk] = request.POST.get(f'pm_declarado_{pm.pk}', '0')
            payment_comentarios[pm.pk] = request.POST.get(f'pm_comentario_{pm.pk}', '')
            declarado_val = Decimal(payment_declared.get(pm.pk, '0'))
            sistema_breakdown = breakdown.get(pm.pk, Decimal('0'))
            payment_diffs[pm.pk] = declarado_val - sistema_breakdown
            total_declarado += declarado_val

        dif_general = total_declarado - summary['total_esperado']
        saldo_real = total_declarado

        return render(request, 'orders/cash_session_close_confirm.html', {
            'session': session,
            'summary': summary,
            'payment_methods': payment_methods,
            'breakdown': breakdown,
            'payment_declared': payment_declared,
            'payment_comentarios': payment_comentarios,
            'payment_diffs': payment_diffs,
            'total_declarado': total_declarado,
            'dif_general': dif_general,
            'saldo_real': saldo_real,
            'comentario_cierre': comentario_cierre,
            'error': str(e),
        })

    return redirect('orders:sesion-detalle', session_id=session_id)


@login_required
def sesiones_cerradas(request):
    """Lista las sesiones de caja cerradas del tenant."""
    sesiones = CashSession.objects.for_tenant(request.tenant).filter(
        estado=CashSession.States.CERRADA,
    ).select_related('cash_register', 'opened_by', 'closed_by')

    return render(request, 'orders/sesiones_cerradas.html', {
        'sesiones': sesiones,
    })