# Generated by Django 3.2.17 on 2023-09-06 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0022_auto_20230906_1337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockhistory',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.category'),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='household',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.household'),
        ),
        migrations.AlterField(
            model_name='stockhistory',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='stockmgmt.location'),
        ),
    ]