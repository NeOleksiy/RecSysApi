# Generated by Django 4.2.7 on 2023-12-07 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recommender', '0004_delete_tfidf_similarity'),
    ]

    operations = [
        migrations.CreateModel(
            name='TfIdfMatrix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_id', models.CharField(db_index=True, max_length=16)),
                ('col_id', models.CharField(max_length=16)),
                ('tfidf_sim', models.DecimalField(decimal_places=7, max_digits=8)),
            ],
            options={
                'db_table': 'tf-idf-matrix',
            },
        ),
    ]