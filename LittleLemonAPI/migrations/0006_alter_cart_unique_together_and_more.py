# Generated by Django 5.0.2 on 2024-03-15 00:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0005_alter_category_title'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('menuitem', 'user')},
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='unit_price',
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='LittleLemonAPI.order'),
        ),
        migrations.RemoveField(
            model_name='cart',
            name='created_at',
        ),
    ]