# Generated by Django 4.2.7 on 2023-11-20 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Similarity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField()),
                ('source', models.CharField(db_index=True, max_length=16)),
                ('target', models.CharField(max_length=16)),
                ('similarity', models.DecimalField(decimal_places=7, max_digits=8)),
            ],
            options={
                'db_table': 'similarity',
            },
        ),
    ]
