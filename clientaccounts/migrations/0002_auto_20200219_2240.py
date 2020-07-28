# Generated by Django 2.2.6 on 2020-02-19 22:40

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clientaccounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientaccount',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='clientaccount',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_document'], name='clientaccou_search__510bbf_gin'),
        ),
    ]