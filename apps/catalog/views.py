from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalog.forms import CategoryForm, ProductForm
from apps.catalog.models import Category, Product
from apps.catalog.selectors.category import CategorySelector
from apps.catalog.selectors.product import ProductSelector
from apps.catalog.services.category import CategoryService
from apps.catalog.services.product import ProductService
from apps.core.services.auth import require_permission


@login_required
def product_list(request):
    """Lista productos del tenant, con búsqueda opcional y agrupados por categoría."""
    require_permission(request.user, 'manage_inventory')
    search_term = request.GET.get('search', '')
    products = ProductSelector.list_for_tenant(request.tenant).filter(inhabilitado=False)
    if search_term:
        products = products.filter(
            Q(nombre__icontains=search_term) | Q(description__icontains=search_term)
        )
    products = products.select_related('category').order_by('-is_active', 'category__nombre', 'nombre')
    categories = CategorySelector.get_active_categories(request.tenant).filter(inhabilitado=False)
    return render(request, 'catalog/product_list.html', {
        'products': products,
        'categories': categories,
        'search_term': search_term,
    })


@login_required
def product_create(request):
    """Crea un nuevo producto para el tenant."""
    require_permission(request.user, 'manage_inventory')
    if request.method == 'POST':
        form = ProductForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            try:
                ProductService.create_product(
                    tenant=request.tenant,
                    category=form.cleaned_data['category'],
                    nombre=form.cleaned_data['nombre'],
                    precio_bruto=form.cleaned_data['precio_bruto'],
                    es_inventariable=form.cleaned_data['es_inventariable'],
                    stock_actual=form.cleaned_data.get('stock_actual'),
                    description=form.cleaned_data.get('description', ''),
                )
                messages.success(request, 'Producto creado exitosamente.')
                return redirect('catalog:product-list')
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = ProductForm(tenant=request.tenant)
    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': 'Crear Producto',
    })


@login_required
def product_edit(request, pk):
    """Edita un producto existente del tenant."""
    require_permission(request.user, 'manage_inventory')
    product = get_object_or_404(Product.objects.for_tenant(request.tenant).filter(inhabilitado=False), pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, tenant=request.tenant, instance=product)
        if form.is_valid():
            try:
                ProductService.update_product(
                    product,
                    nombre=form.cleaned_data['nombre'],
                    precio_bruto=form.cleaned_data['precio_bruto'],
                    es_inventariable=form.cleaned_data['es_inventariable'],
                    category=form.cleaned_data['category'],
                    description=form.cleaned_data.get('description', ''),
                    stock_actual=form.cleaned_data.get('stock_actual'),
                )
                messages.success(request, 'Producto actualizado exitosamente.')
                return redirect('catalog:product-list')
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = ProductForm(tenant=request.tenant, instance=product)
    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': 'Editar Producto',
    })


@login_required
def product_toggle_active(request, pk):
    """Pausa o reanuda un producto (desactivación temporal)."""
    require_permission(request.user, 'manage_inventory')
    product = get_object_or_404(Product.objects.for_tenant(request.tenant).filter(inhabilitado=False), pk=pk)
    if request.method != 'POST':
        return redirect('catalog:product-list')
    ProductService.toggle_active(product)
    estado = "pausado" if not product.is_active else "reactivado"
    messages.success(request, f'Producto {estado}.')
    return redirect('catalog:product-list')


@login_required
def product_inhabilitar(request, pk):
    """Inhabilita permanentemente un producto (no se puede reactivar)."""
    require_permission(request.user, 'manage_inventory')
    product = get_object_or_404(Product.objects.for_tenant(request.tenant), pk=pk)
    if request.method != 'POST':
        return redirect('catalog:product-list')
    product.inhabilitado = True
    product.is_active = False
    product.save(update_fields=['inhabilitado', 'is_active'])
    messages.success(request, 'Producto inhabilitado permanentemente.')
    return redirect('catalog:product-list')


@login_required
def category_list(request):
    """Lista categorías del tenant."""
    require_permission(request.user, 'manage_inventory')
    categories = CategorySelector.list_for_tenant(request.tenant).filter(inhabilitado=False)
    return render(request, 'catalog/category_list.html', {
        'categories': categories.order_by('-is_active', 'nombre'),
    })


@login_required
def category_create(request):
    """Crea una nueva categoría para el tenant."""
    require_permission(request.user, 'manage_inventory')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                CategoryService.create_category(
                    tenant=request.tenant,
                    nombre=form.cleaned_data['nombre'],
                )
                messages.success(request, 'Categoría creada exitosamente.')
                return redirect('catalog:category-list')
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = CategoryForm()
    return render(request, 'catalog/category_form.html', {
        'form': form,
        'title': 'Crear Categoría',
    })


@login_required
def category_edit(request, pk):
    """Edita una categoría existente del tenant."""
    require_permission(request.user, 'manage_inventory')
    category = get_object_or_404(Category.objects.for_tenant(request.tenant).filter(inhabilitado=False), pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                CategoryService.update_category(category, nombre=form.cleaned_data['nombre'])
                messages.success(request, 'Categoría actualizada exitosamente.')
                return redirect('catalog:category-list')
            except ValidationError as e:
                form.add_error(None, str(e))
    else:
        form = CategoryForm(instance=category)
    return render(request, 'catalog/category_form.html', {
        'form': form,
        'title': 'Editar Categoría',
    })


@login_required
def category_toggle_active(request, pk):
    """Pausa o reanuda una categoría (desactivación temporal)."""
    require_permission(request.user, 'manage_inventory')
    category = get_object_or_404(Category.objects.for_tenant(request.tenant).filter(inhabilitado=False), pk=pk)
    if request.method != 'POST':
        return redirect('catalog:category-list')
    CategoryService.toggle_active(category)
    estado = "pausada" if not category.is_active else "reactivada"
    messages.success(request, f'Categoría {estado}.')
    return redirect('catalog:category-list')


@login_required
def category_inhabilitar(request, pk):
    """Inhabilita permanentemente una categoría (no se puede reactivar)."""
    require_permission(request.user, 'manage_inventory')
    category = get_object_or_404(Category.objects.for_tenant(request.tenant), pk=pk)
    if request.method != 'POST':
        return redirect('catalog:category-list')
    category.inhabilitado = True
    category.is_active = False
    category.save(update_fields=['inhabilitado', 'is_active'])
    messages.success(request, 'Categoría inhabilitada permanentemente.')
    return redirect('catalog:category-list')


@login_required
def category_select_modal(request):
    """Modal para seleccionar o crear categorías desde formularios de producto."""
    require_permission(request.user, 'manage_inventory')
    error = None
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            try:
                CategoryService.create_category(tenant=request.tenant, nombre=nombre)
                messages.success(request, f'Categoría "{nombre}" creada.')
            except ValidationError as e:
                error = str(e)
        else:
            error = 'El nombre es obligatorio.'
    categories = Category.objects.for_tenant(request.tenant).filter(inhabilitado=False, is_active=True)
    return render(request, 'catalog/partials/category_select_modal.html', {
        'categories': categories,
        'error': error,
    })
