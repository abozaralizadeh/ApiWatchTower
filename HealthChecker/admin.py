from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(HealthCheckRule)
class HealthCheckRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'http_method', 'url', 'enable')

@admin.register(HealthCheckRecord)
class HealthCheckRecordAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "timestamp", "response_code", "response_body", "response_delay", "health_check_rule", "success", "error"]
    fields = ('id', 'health_check_rule',('response_code', 'response_body'), 'response_delay', 'success', 'timestamp', 'error', 'error_description')
    list_display = ('id', 'health_check_rule', 'response_code', 'response_delay', 'success', 'timestamp')
    search_fields = ['id', 'health_check_rule']
    list_filter = ('health_check_rule', 'response_code', 'success')

@admin.register(ClientCertificate)
class ClientCertificateAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Header)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')