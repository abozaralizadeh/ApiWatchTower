# Generated by Django 2.2.14 on 2020-07-05 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('HealthChecker', '0003_auto_20200705_1016'),
    ]

    operations = [
        migrations.CreateModel(
            name='Header',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='HealthCheckRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('response_code', models.CharField(blank=True, editable=False, max_length=8, null=True)),
                ('response_body', models.TextField(blank=True, editable=False, null=True)),
                ('response_delay', models.FloatField(blank=True, editable=False, null=True)),
                ('success', models.BooleanField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='HealthCheckRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=4096)),
                ('http_method', models.CharField(choices=[('get', 'GET'), ('post', 'POST')], default='get', max_length=8)),
                ('request_body', models.TextField(blank=True, null=True)),
                ('expected_response_code', models.CharField(blank=True, help_text='Regular Expression', max_length=8, null=True)),
                ('expected_response_body', models.TextField(blank=True, help_text='Regular Expression', null=True)),
                ('enable', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='HealthCheckRules',
        ),
        migrations.AlterField(
            model_name='clientcertificate',
            name='client_cert',
            field=models.FileField(blank=True, help_text='Use .pem cert file', null=True, upload_to='certificates/'),
        ),
        migrations.AlterField(
            model_name='clientcertificate',
            name='client_key',
            field=models.FileField(blank=True, help_text='Use .pem key file', null=True, upload_to='certificates/'),
        ),
        migrations.AddField(
            model_name='healthcheckrule',
            name='client_certificate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='HealthChecker.ClientCertificate'),
        ),
        migrations.AddField(
            model_name='healthcheckrule',
            name='headers',
            field=models.ManyToManyField(blank=True, to='HealthChecker.Header'),
        ),
        migrations.AddField(
            model_name='healthcheckrecord',
            name='health_check_rule',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='HealthChecker.HealthCheckRule'),
        ),
    ]
