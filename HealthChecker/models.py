from django.db import models


class Header(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=1024)

    def __str__(self):
        return self.key + " : " + self.value

class ClientCertificate(models.Model):
    name = models.CharField(max_length=100)
    client_cert = models.FileField(help_text='Use .pem cert file', upload_to='certificates/')
    client_key = models.FileField(help_text='Use .pem key file', upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return self.name

class HealthCheckRule(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=4096)
    http_method = models.CharField(
        max_length=8,
        choices=[
            ('get', 'GET'),
            ('post', 'POST')
        ],
        default='get',
    )
    headers = models.ManyToManyField(Header, blank=True)
    request_body = models.TextField(blank=True, null=True)
    client_certificate = models.ForeignKey(ClientCertificate, on_delete=models.SET_NULL, blank=True, null=True)
    expected_response_code = models.CharField(max_length=8, help_text='Regular Expression', default='200', blank=True, null=True)
    expected_response_body = models.TextField(help_text='Regular Expression', default='.*', blank=True, null=True)
    enable = models.BooleanField(default=True)
    output_variables = models.TextField(help_text='keys seperated by comma', default='', blank=True, null=True)
    run_after = models.ForeignKey('HealthCheckRule', on_delete=models.SET_NULL, related_name='nexts', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class HealthCheckRecord(models.Model):
    request = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    response_code = models.CharField(max_length=8, blank=True, null=True)
    response_body = models.TextField(blank=True, null=True)
    response_delay = models.FloatField(blank=True, null=True)
    health_check_rule = models.ForeignKey(HealthCheckRule, on_delete=models.SET_NULL, blank=True, null=True)
    success = models.BooleanField(blank=True, null=True)
    error = models.BooleanField(blank=True, null=True)
    error_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.health_check_rule.name + " " + str(self.success) + " " + str(self.timestamp)