# Generated by Django 3.2.17 on 2023-08-27 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0012_alter_stockhistory_household'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockhistory',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.location'),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.room'),
        ),
    ]
