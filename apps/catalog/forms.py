from django import forms

from apps.catalog.models import Category, Product


class CLPNumberInput(forms.NumberInput):
    """Widget numérico que formatea sin decimales y con separador de miles como punto.

    Ejemplo: 15000 se muestra como 15.000
    """

    def format_value(self, value):
        if value in (None, ''):
            return ''
        try:
            return f'{int(value):,}'.replace(',', '.')
        except (ValueError, TypeError):
            return value


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['nombre']
        labels = {
            'nombre': 'Nombre',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nombre', 'category', 'precio_bruto', 'es_inventariable', 'stock_actual', 'description']
        labels = {
            'nombre': 'Nombre',
            'category': 'Categoría',
            'precio_bruto': 'Precio',
            'es_inventariable': 'Es inventariable',
            'stock_actual': 'Stock actual',
            'description': 'Descripción',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'precio_bruto': CLPNumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'}),
            'es_inventariable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'stock_actual': CLPNumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['category'].queryset = Category.objects.for_tenant(tenant).filter(inhabilitado=False)
