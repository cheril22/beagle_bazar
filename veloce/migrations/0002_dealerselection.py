# Generated by Django 3.2.7 on 2021-11-30 07:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('veloce', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DealerSelection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pin_code', models.CharField(blank=True, max_length=6, null=True)),
                ('city', models.CharField(blank=True, max_length=40, null=True)),
                ('state', models.CharField(blank=True, max_length=55, null=True)),
                ('is_pending', models.BooleanField(blank=True, default=True, null=True)),
                ('dealer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Profile', to=settings.AUTH_USER_MODEL)),
                ('institution', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ProductRating', to=settings.AUTH_USER_MODEL)),
                ('product', models.ManyToManyField(related_name='product', to='veloce.Product')),
            ],
        ),
    ]
