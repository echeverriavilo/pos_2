from django import forms

from apps.orders.models import PaymentMethod


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['nombre', 'orden']
        labels = {
            'nombre': 'Nombre',
            'orden': 'Orden',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del método de pago'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }
