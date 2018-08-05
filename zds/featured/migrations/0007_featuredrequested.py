# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2018-08-04 21:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('featured', '0006_python_3'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedRequested',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('type', models.CharField(choices=[('CONTENT', 'Contenu'), ('TOPIC', 'Topic')], db_index=True, max_length=10)),
                ('rejected', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('featured', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='featured.FeaturedResource')),
                ('users_voted', models.ManyToManyField(blank=True, db_index=True, to=settings.AUTH_USER_MODEL, verbose_name='Auteurs')),
            ],
            options={
                'verbose_name': 'Mise en avant souhaitée',
                'verbose_name_plural': 'Mises en avant souhaitées',
            },
        ),
    ]