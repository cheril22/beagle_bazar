# Generated by Django 3.2.7 on 2021-12-03 05:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('veloce', '0003_alter_dealerselection_institution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dealerselection',
            name='product',
        ),
        migrations.AddField(
            model_name='dealerselection',
            name='by_whom',
            field=models.CharField(blank=True, max_length=70, null=True),
        ),
        migrations.AddField(
            model_name='dealerselection',
            name='is_application_rejected',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='dealerselection',
            name='reject_reason',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.CreateModel(
            name='SelectProductByDealer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_product_rejected', models.BooleanField(blank=True, default=False, null=True)),
                ('by_whom', models.CharField(blank=True, max_length=70, null=True)),
                ('reject_reason', models.CharField(blank=True, max_length=256, null=True)),
                ('dealerselection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='veloce.dealerselection')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product', to='veloce.product')),
            ],
        ),
    ]
