# Generated by Django 4.2.7 on 2023-11-19 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productApi', '0008_remove_anime_id_alter_anime_anime_id'),
        ('collector', '0002_alter_conversion_content_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversion',
            name='content_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='productApi.anime'),
        ),
    ]
