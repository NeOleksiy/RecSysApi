# Generated by Django 4.2.7 on 2023-11-19 16:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('productApi', '0006_cluster'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('event', models.CharField(choices=[('open site', 'Open Site'), ('Opened another page of the site', 'Open New Page'), ('open the product page', 'Open Product Page'), ('add to list', 'Add To List'), ('watched', 'Watched'), ('rated', 'Rated')], max_length=200)),
                ('content_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productApi.anime')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
