# Generated by Django 3.1.7 on 2022-10-30 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TermAndQuestion',
            fields=[
                ('questionID', models.AutoField(primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('termID', models.ForeignKey(db_column='termID', on_delete=django.db.models.deletion.DO_NOTHING, to='backend.investopediaterms')),
            ],
            options={
                'db_table': 'Investopedia_Term_Question',
                'managed': True,
            },
        ),
    ]
