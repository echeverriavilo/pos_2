# Generated migration for Transaction tip_amount and payment_method fields

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_paymentmethod'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='payment_method',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='transactions',
                to='orders.paymentmethod',
            ),
        ),
        migrations.AddField(
            model_name='transaction',
            name='tip_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
    ]
