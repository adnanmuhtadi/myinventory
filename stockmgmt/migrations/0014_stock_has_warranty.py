# Generated by Django 3.2.17 on 2023-08-30 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmt', '0013_auto_20230827_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='has_warranty',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
