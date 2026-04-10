from decimal import Decimal

import pytest

from apps.core import tenant_context
from apps.core.services import tenant as tenant_service
from apps.catalog.models import Category, Product, Ingredient, StockMovement
from apps.catalog.services import (
    CategoryService,
    ProductService,
    IngredientService,
    InventoryService,
)
from apps.catalog.selectors import (
    CategorySelector,
    ProductSelector,
    IngredientSelector,
    StockMovementSelector,
)
from apps.catalog.services.inventory import InventoryError


@pytest.mark.django_db
def test_catalog_entities_are_tenant_scoped():
    tenant_a = tenant_service.TenantService.create_tenant(slug='tenant-a', name='Tenant A')
    tenant_b = tenant_service.TenantService.create_tenant(slug='tenant-b', name='Tenant B')

    with tenant_context.tenant_scope(tenant_a):
        category_a = CategoryService.create_category(tenant=tenant_a, nombre='Bebidas')
        product_a = ProductService.create_product(
            tenant=tenant_a,
            category=category_a,
            nombre='Jugo natural',
            precio_bruto=Decimal('4.50'),
        )
        ingredient = IngredientService.create_ingredient(tenant=tenant_a, nombre='Fruta fresca')

    with tenant_context.tenant_scope(tenant_b):
        category_b = CategoryService.create_category(tenant=tenant_b, nombre='Postres')

    with tenant_context.tenant_scope(tenant_a):
        assert CategorySelector.list_for_tenant(tenant_a).first() == category_a
        assert ProductSelector.list_for_tenant(tenant_a).first() == product_a
        assert IngredientSelector.list_for_tenant(tenant_a).first() == ingredient
        assert product_a.category == category_a

    with tenant_context.tenant_scope(tenant_b):
        assert CategorySelector.list_for_tenant(tenant_b).first() == category_b
        assert ProductSelector.list_for_tenant(tenant_b).count() == 0


@pytest.mark.django_db
def test_inventory_records_movements_and_updates_stock():
    tenant = tenant_service.TenantService.create_tenant(slug='inventory', name='Inventario')
    with tenant_context.tenant_scope(tenant):
        cat = CategoryService.create_category(tenant=tenant, nombre='Salados')
        product = ProductService.create_product(
            tenant=tenant,
            category=cat,
            nombre='Empanada',
            precio_bruto=Decimal('2.50'),
            stock_actual=Decimal('5.00'),
        )

        InventoryService.registrar_ingreso(product=product, cantidad=Decimal('10.00'))
        InventoryService.registrar_ajuste(product=product, cantidad=Decimal('-2.50'))
        InventoryService.registrar_venta(product=product, cantidad=Decimal('3.00'))

        product.refresh_from_db()
        assert product.stock_actual == Decimal('9.50')
        movimientos = StockMovementSelector.list_for_product(product)
        assert movimientos.count() == 3
        assert movimientos.first().tipo == StockMovement.Types.VENTA


@pytest.mark.django_db
def test_inventory_blocks_negative_stock_for_inventariables():
    tenant = tenant_service.TenantService.create_tenant(slug='inventario-negativo', name='Inventario Negativo')
    with tenant_context.tenant_scope(tenant):
        cat = CategoryService.create_category(tenant=tenant, nombre='Platos')
        product = ProductService.create_product(
            tenant=tenant,
            category=cat,
            nombre='Asado',
            precio_bruto=Decimal('20.00'),
            stock_actual=Decimal('1.00'),
        )
        with pytest.raises(InventoryError):
            InventoryService.registrar_venta(product=product, cantidad=Decimal('2.00'))


@pytest.mark.django_db
def test_inventory_allows_negative_stock_for_non_inventariables():
    tenant = tenant_service.TenantService.create_tenant(slug='no-inventario', name='No Inventario')
    with tenant_context.tenant_scope(tenant):
        cat = CategoryService.create_category(tenant=tenant, nombre='Servicios')
        product = ProductService.create_product(
            tenant=tenant,
            category=cat,
            nombre='Servicio expres',
            precio_bruto=Decimal('15.00'),
            es_inventariable=False,
            stock_actual=Decimal('0'),
        )
        InventoryService.registrar_venta(product=product, cantidad=Decimal('5.00'))
        product.refresh_from_db()
        assert product.stock_actual == Decimal('-5.00')
