import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('orders', '0002_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=12)),
                ('tipo_pago', models.CharField(choices=[('TOTAL', 'Total'), ('ABONO', 'Abono'), ('PRODUCTOS', 'Productos')], max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='orders.order')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='core.tenant')),
            ],
            options={
                'ordering': ('-created_at', '-id'),
            },
        ),
        migrations.CreateModel(
            name='TransactionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transaction_items', to='orders.orderitem')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_items', to='core.tenant')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.transaction')),
            ],
            options={
                'ordering': ('created_at', 'id'),
                'unique_together': {('tenant', 'order_item'), ('transaction', 'order_item')},
            },
        ),
    ]
