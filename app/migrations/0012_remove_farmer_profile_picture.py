# Generated by Django 5.0.3 on 2024-10-24 19:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_alter_farmer_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='farmer',
            name='profile_picture',
        ),
    ]
