# Generated by Django 2.2.17 on 2020-12-17 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthChecker', '0010_healthcheckrule_output_variables'),
    ]

    operations = [
        migrations.AddField(
            model_name='healthcheckrecord',
            name='request',
            field=models.TextField(blank=True, null=True),
        ),
    ]
