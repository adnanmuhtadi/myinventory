# Generated by Django 3.2.17 on 2023-09-06 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0021_alter_stockhistory_household'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockhistory',
            name='category',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.category'),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='location',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.location'),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='room',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.room'),
        ),
    ]
