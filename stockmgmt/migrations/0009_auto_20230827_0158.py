# Generated by Django 3.2.17 on 2023-08-27 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0008_alter_stockhistory_reorder_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='reorder_level',
            field=models.IntegerField(blank=True, default='3', null=True),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='reorder_level',
            field=models.IntegerField(blank=True, default='0', null=True),
        ),
    ]
