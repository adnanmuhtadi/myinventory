# Generated by Django 3.2.17 on 2023-09-07 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0033_auto_20230907_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='item_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]