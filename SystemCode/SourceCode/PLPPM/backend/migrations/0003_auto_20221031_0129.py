# Generated by Django 3.1.7 on 2022-10-30 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_termandquestion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='investopediaterms',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='termandquestion',
            options={'managed': False},
        ),
    ]
