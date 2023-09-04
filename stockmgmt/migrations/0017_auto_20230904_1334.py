# Generated by Django 3.2.17 on 2023-09-04 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0016_remove_stock_total_issued_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='issue_reason',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.DeleteModel(
            name='StockHistory',
        ),
    ]
