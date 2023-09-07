# Generated by Django 3.2.17 on 2023-09-07 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0034_alter_stock_item_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stockhistory',
            name='household',
        ),
        migrations.RemoveField(
            model_name='stockhistory',
            name='location',
        ),
        migrations.RemoveField(
            model_name='stockhistory',
            name='room',
        ),
        migrations.AlterField(
            model_name='stock',
            name='item_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
