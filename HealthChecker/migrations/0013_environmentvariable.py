# Generated by Django 2.2.19 on 2021-04-02 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthChecker', '0012_healthcheckrule_run_after'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnvironmentVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=1024)),
            ],
        ),
    ]
