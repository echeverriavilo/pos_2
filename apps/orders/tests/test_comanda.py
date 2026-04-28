import pytest
from decimal import Decimal

from apps.catalog.models import Category, Product
from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission, Tenant
from apps.core.tenant_context import tenant_scope
from apps.dining.models import DiningTable
from apps.orders.models import Dispositivo, ConfiguracionDispositivo, Comanda, Order, OrderItem, PaymentMethod
from apps.orders.services import (
    DispositivoService,
    DispositivoError,
    ComandaService,
    ComandaError,
    create_order,
    add_or_update_item_in_order,
    transition_order_state,
)


def _create_admin_user(tenant):
    """Crea un usuario Administrador con permisos completos."""
    user = CustomUser.objects.create_user(email=f'admin@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='administrador')
    all_perms = [
        'create_order', 'add_item', 'remove_item', 'register_payment',
        'manage_inventory', 'manage_users', 'manage_tables', 'manage_devices'
    ]
    for perm_codename in all_perms:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        RolePermission.objects.get_or_create(role=role, permission=perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


def _create_payment_method(tenant):
    return PaymentMethod.objects.create(tenant=tenant, nombre='Efectivo', orden=0, activo=True)


@pytest.mark.django_db
def test_flujo_mesa_genera_comanda_al_agregar_item():
    """Test que en flujo MESA se genera comanda al agregar item."""
    tenant = Tenant.objects.create(slug='test-mesa-comanda', name='Test Mesa Comanda')
    user = _create_admin_user(tenant)
    
    with tenant_scope(tenant):
        dispositivo = DispositivoService.create_dispositivo(
            user=user, tenant=tenant, nombre='Cocina', tipo=Dispositivo.Tipo.PANTALLA
        )
        
        category = Category.objects.create(tenant=tenant, nombre='Comida')
        product = Product.objects.create(
            tenant=tenant, category=category, nombre='Hamburguesa',
            precio_bruto=Decimal('5000'), es_inventariable=False
        )
        
        table = DiningTable.objects.create(tenant=tenant, numero='1')
        order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
        item = add_or_update_item_in_order(user=user, order=order, product=product, cantidad=2)
        
        comandas = Comanda.objects.for_tenant(tenant).filter(orden=order)
        assert comandas.count() >= 1
        
        comanda = comandas.first()
        assert comanda.items.filter(order_item=item).exists()
        assert comanda.estado == Comanda.Estado.PENDIENTE


@pytest.mark.django_db
def test_flujo_rapido_genera_comandas_al_confirmar():
    """Test que en flujo rápido se genera comanda al confirmar pedido (después de pago)."""
    tenant = Tenant.objects.create(slug='test-rapido-comanda', name='Test Rapido Comanda')
    user = _create_admin_user(tenant)
    
    with tenant_scope(tenant):
        dispositivo = DispositivoService.create_dispositivo(
            user=user, tenant=tenant, nombre='Barra', tipo=Dispositivo.Tipo.PANTALLA
        )
        
        category = Category.objects.create(tenant=tenant, nombre='Bebidas')
        product = Product.objects.create(
            tenant=tenant, category=category, nombre='Cerveza',
            precio_bruto=Decimal('3000'), es_inventariable=False
        )
        
        order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.RAPIDO)
        item = add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
        
        assert Comanda.objects.for_tenant(tenant).filter(orden=order).count() == 0
        
        from apps.orders.services.payment import register_transaction
        from apps.orders.models import Transaction
        
        payment_method = _create_payment_method(tenant)
        register_transaction(
            user=user,
            tenant=tenant,
            order=order,
            payment_type=Transaction.PaymentType.TOTAL,
            payment_method=payment_method,
        )
        
        comandas = Comanda.objects.for_tenant(tenant).filter(orden=order)
        assert comandas.count() >= 1
        comanda = comandas.first()
        assert comanda.items.filter(order_item=item).exists()


@pytest.mark.django_db
def test_dispositivo_inactivo_no_recibe_comandas():
    """Test que dispositivos inactivos no reciben comandas."""
    tenant = Tenant.objects.create(slug='test-inactivo', name='Test Inactivo')
    user = _create_admin_user(tenant)
    
    with tenant_scope(tenant):
        dispositivo_activo = DispositivoService.create_dispositivo(
            user=user, tenant=tenant, nombre='Activo', tipo=Dispositivo.Tipo.PANTALLA
        )
        dispositivo_inactivo = DispositivoService.create_dispositivo(
            user=user, tenant=tenant, nombre='Inactivo', tipo=Dispositivo.Tipo.PANTALLA, activo=False
        )
        
        category = Category.objects.create(tenant=tenant, nombre='Test')
        product = Product.objects.create(
            tenant=tenant, category=category, nombre='Producto Test',
            precio_bruto=Decimal('1000'), es_inventariable=False
        )
        
        ConfiguracionDispositivo.objects.create(
            tenant=tenant, dispositivo=dispositivo_activo, producto=product, prioridad=1
        )
        ConfiguracionDispositivo.objects.create(
            tenant=tenant, dispositivo=dispositivo_inactivo, producto=product, prioridad=1
        )
        
        table = DiningTable.objects.create(tenant=tenant, numero='1')
        order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
        add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
        
        comandas = Comanda.objects.for_tenant(tenant).filter(orden=order)
        assert comandas.filter(dispositivo=dispositivo_activo).exists()
        assert not comandas.filter(dispositivo=dispositivo_inactivo).exists()


@pytest.mark.django_db
def test_transiciones_estado_comanda_validas():
    """Test transiciones válidas de estado de comanda."""
    tenant = Tenant.objects.create(slug='test-trans', name='Test Transiciones')
    user = _create_admin_user(tenant)
    
    with tenant_scope(tenant):
        dispositivo = DispositivoService.create_dispositivo(
            user=user, tenant=tenant, nombre='Cocina', tipo=Dispositivo.Tipo.PANTALLA
        )
        
        category = Category.objects.create(tenant=tenant, nombre='Test')
        product = Product.objects.create(
            tenant=tenant, category=category, nombre='Test',
            precio_bruto=Decimal('1000'), es_inventariable=False
        )
        
        table = DiningTable.objects.create(tenant=tenant, numero='1')
        order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
        item = add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
        
        comanda = Comanda.objects.for_tenant(tenant).filter(orden=order).first()
        assert comanda is not None, "La comanda debería existir"
        
        updated = ComandaService.actualizar_estado_comanda(
            user=user, comanda=comanda, estado=Comanda.Estado.LISTA
        )
        assert updated.estado == Comanda.Estado.LISTA
        
        updated = ComandaService.actualizar_estado_comanda(
            user=user, comanda=comanda, estado=Comanda.Estado.ENTREGADO
        )
        assert updated.estado == Comanda.Estado.ENTREGADO


@pytest.mark.django_db
def test_transiciones_estado_comanda_invalidas_lanzan_error():
    """Test que transiciones inválidas lanzan error."""
    tenant = Tenant.objects.create(slug='test-invalid', name='Test Invalid')
    user = _create_admin_user(tenant)
    
    with tenant_scope(tenant):
        dispositivo = DispositivoService.create_dispositivo(
            user=user, tenant=tenant, nombre='Cocina', tipo=Dispositivo.Tipo.PANTALLA
        )
        
        category = Category.objects.create(tenant=tenant, nombre='Test')
        product = Product.objects.create(
            tenant=tenant, category=category, nombre='Test',
            precio_bruto=Decimal('1000'), es_inventariable=False
        )
        
        table = DiningTable.objects.create(tenant=tenant, numero='1')
        order = create_order(user=user, tenant=tenant, tipo_flujo=Order.Flow.MESA, table=table)
        add_or_update_item_in_order(user=user, order=order, product=product, cantidad=1)
        
        comanda = Comanda.objects.for_tenant(tenant).filter(orden=order).first()
        assert comanda is not None, "La comanda debería existir"
        
        with pytest.raises(ComandaError):
            ComandaService.actualizar_estado_comanda(
                user=user, comanda=comanda, estado=Comanda.Estado.ENTREGADO
            )


@pytest.mark.django_db
def test_create_dispositivo():
    """Test de creación de dispositivo."""
    tenant = Tenant.objects.create(slug='test-device', name='Test Device Tenant')
    user = _create_admin_user(tenant)
    
    dispositivo = DispositivoService.create_dispositivo(
        user=user,
        tenant=tenant,
        nombre='Cocina Principal',
        tipo=Dispositivo.Tipo.IMPRESORA
    )
    
    assert dispositivo.nombre == 'Cocina Principal'
    assert dispositivo.tipo == Dispositivo.Tipo.IMPRESORA
    assert dispositivo.activo is True
    assert dispositivo.tenant == tenant


@pytest.mark.django_db
def test_update_dispositivo():
    """Test de actualización de dispositivo."""
    tenant = Tenant.objects.create(slug='test-update-device', name='Test Update Device')
    user = _create_admin_user(tenant)
    
    dispositivo = DispositivoService.create_dispositivo(
        user=user, tenant=tenant, nombre='Barra', tipo=Dispositivo.Tipo.PANTALLA
    )
    
    updated = DispositivoService.update_dispositivo(
        user=user, dispositivo=dispositivo, activo=False
    )
    
    assert updated.activo is False


@pytest.mark.django_db
def test_configuracion_producto_tiene_prioridad_sobre_categoria():
    """Test que la configuración de producto tiene mayor prioridad que la de categoría."""
    tenant = Tenant.objects.create(slug='test-priority', name='Test Priority')
    user = _create_admin_user(tenant)
    
    # Crear dispositivo
    dispositivo = DispositivoService.create_dispositivo(
        user=user, tenant=tenant, nombre='Cocina', tipo=Dispositivo.Tipo.IMPRESORA
    )
    
    # Crear categoría y producto
    category = Category.objects.create(tenant=tenant, nombre='Bebidas')
    product = Product.objects.create(
        tenant=tenant, category=category, nombre='Café',
        precio_bruto=Decimal('1000'), es_inventariable=False
    )
    
    # Crear config de categoría (baja prioridad)
    config_cat = ConfiguracionDispositivo.objects.create(
        tenant=tenant, dispositivo=dispositivo, categoria=category, prioridad=1
    )
    
    # Crear config de producto (alta prioridad)
    config_prod = ConfiguracionDispositivo.objects.create(
        tenant=tenant, dispositivo=dispositivo, producto=product, prioridad=10
    )
    
    # Verificar que la config de producto se selecciona primero
    from apps.orders.selectors import ConfiguracionDispositivoSelector
    effective = ConfiguracionDispositivoSelector.get_effective_configuration_for_product(tenant, product)
    
    assert effective == config_prod
