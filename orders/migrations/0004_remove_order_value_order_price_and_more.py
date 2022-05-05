# Generated by Django 4.0.4 on 2022-05-05 02:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payment_created_payment_updated'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0003_product_quantity_product_supplier_price_and_more'),
        ('orders', '0003_alter_orderproduct_order_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='value',
        ),
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payments.payment'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='order_id',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='orders.order'),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='product_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.product'),
        ),
    ]
