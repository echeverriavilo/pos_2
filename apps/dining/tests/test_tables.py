import pytest

from apps.core.models import CustomUser, Membership, Permission, Role, Tenant
from apps.core.services import tenant as tenant_service
from apps.dining.models import DiningTable
from apps.dining.selectors import DiningTableSelector
from apps.dining.services import DiningTableError, DiningTableService
from apps.orders.models import Order


def _create_garzon_user(tenant):
    user = CustomUser.objects.create_user(email=f'garzon@{tenant.slug}.com', password='test123')
    role = Role.objects.create(tenant=tenant, name='garzon')
    for perm_codename in ['create_order', 'add_item', 'manage_tables']:
        perm, _ = Permission.objects.get_or_create(codename=perm_codename)
        role.permissions.add(perm)
    Membership.objects.create(user=user, tenant=tenant, role=role)
    return user


@pytest.mark.django_db
def test_open_table_creates_order_and_sets_estado_ocupada():
    tenant = tenant_service.TenantService.create_tenant(slug='mesa-flow', name='Mesa Flow', config_flujo_mesas=True)
    user = _create_garzon_user(tenant)
    table = DiningTableService.create_table(user=user, tenant=tenant, numero='10')
    assert table.estado == DiningTable.States.DISPONIBLE

    order = DiningTableService.open_table(user=user, table=table)
    table.refresh_from_db()

    assert table.estado == DiningTable.States.OCUPADA
    assert order.estado == Order.States.ABIERTO
    assert DiningTableSelector.get_active_order_for_table(table) == order


@pytest.mark.django_db
def test_open_table_requires_available_state_and_no_active_order():
    tenant = tenant_service.TenantService.create_tenant(slug='mesa-flujo-2', name='Otro Flujo', config_flujo_mesas=True)
    user = _create_garzon_user(tenant)
    table = DiningTableService.create_table(user=user, tenant=tenant, numero='11')
    DiningTableService.open_table(user=user, table=table)

    with pytest.raises(DiningTableError):
        DiningTableService.open_table(user=user, table=table)

    table.estado = DiningTable.States.PAGANDO
    table.save(update_fields=['estado'])
    with pytest.raises(DiningTableError):
        DiningTableService.open_table(user=user, table=table)


@pytest.mark.django_db
def test_set_table_paying_requires_active_order():
    tenant = tenant_service.TenantService.create_tenant(slug='mesa-flow-3', name='Flujo 3', config_flujo_mesas=True)
    user = _create_garzon_user(tenant)
    table = DiningTableService.create_table(user=user, tenant=tenant, numero='12')

    with pytest.raises(DiningTableError):
        DiningTableService.set_table_paying(user=user, table=table)

    order = DiningTableService.open_table(user=user, table=table)
    table.refresh_from_db()
    assert table.estado == DiningTable.States.OCUPADA

    DiningTableService.set_table_paying(user=user, table=table)
    table.refresh_from_db()
    assert table.estado == DiningTable.States.PAGANDO
    assert DiningTableSelector.get_active_order_for_table(table) == order


@pytest.mark.django_db
def test_reopen_table_requires_paying_state_and_active_order():
    tenant = tenant_service.TenantService.create_tenant(slug='mesa-flow-4', name='Flujo 4', config_flujo_mesas=True)
    user = _create_garzon_user(tenant)
    table = DiningTableService.create_table(user=user, tenant=tenant, numero='13')
    order = DiningTableService.open_table(user=user, table=table)
    DiningTableService.set_table_paying(user=user, table=table)
    table.refresh_from_db()

    reopened = DiningTableService.reopen_table(user=user, table=table)
    table.refresh_from_db()

    assert reopened.pk == table.pk
    assert table.estado == DiningTable.States.OCUPADA
    assert DiningTableSelector.get_active_order_for_table(table) == order

    table.estado = DiningTable.States.DISPONIBLE
    table.save(update_fields=['estado'])
    with pytest.raises(DiningTableError):
        DiningTableService.reopen_table(user=user, table=table)