# Generated by Django 4.2.7 on 2023-11-13 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productApi', '0004_alter_anime_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anime',
            name='rating',
            field=models.DecimalField(decimal_places=1, max_digits=3),
        ),
    ]
