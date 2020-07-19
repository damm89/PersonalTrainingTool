# Generated by Django 2.2.6 on 2020-02-19 22:40

from django.conf import settings
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('meals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clientaccounts', '0002_auto_20200219_2240'),
        ('mealplans', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealplantemplate',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mealplan',
            name='client_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientaccounts.ClientAccount'),
        ),
        migrations.AddField(
            model_name='mealplan',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mealmealplantemplate',
            name='day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mealplans.DayMealPlanTemplate'),
        ),
        migrations.AddField(
            model_name='mealmealplantemplate',
            name='meal_categories',
            field=models.ManyToManyField(to='meals.MealCategory'),
        ),
        migrations.AddField(
            model_name='mealmealplantemplate',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='daymealplantemplate',
            name='mealplantemplate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mealplans.MealPlanTemplate'),
        ),
        migrations.AddField(
            model_name='daymealplantemplate',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='mealplantemplate',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_document'], name='mealplans_m_search__a39ae2_gin'),
        ),
        migrations.AddIndex(
            model_name='mealplan',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_document'], name='mealplans_m_search__ddf99e_gin'),
        ),
    ]
