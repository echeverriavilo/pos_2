from django import forms

from apps.core.models import CustomUser, Membership, Role


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del rol'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
        }


class UserForm(forms.ModelForm):
    """Formulario para crear/editar usuarios del tenant."""
    role = forms.ModelChoiceField(
        queryset=Role.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Rol',
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña (solo para crear)'}),
        label='Contraseña',
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name']
        labels = {
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@ejemplo.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['role'].queryset = Role.objects.for_tenant(tenant).filter(inhabilitado=False)
