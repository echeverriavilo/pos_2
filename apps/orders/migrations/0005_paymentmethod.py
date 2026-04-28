# Generated migration for PaymentMethod model

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rolepermission_active_rolepermission_updated_at_and_more'),
        ('orders', '0004_dispositivo_comanda_comandaitem_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('activo', models.BooleanField(default=True)),
                ('orden', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to='core.tenant')),
            ],
            options={
                'ordering': ('orden', 'nombre'),
                'unique_together': {('tenant', 'nombre')},
            },
        ),
    ]
