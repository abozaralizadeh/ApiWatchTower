from django.contrib import admin
from .models import *
from django.utils.translation import gettext


def enable_all(modeladmin, request, queryset):
    queryset.update(enable=True)


enable_all.short_description = gettext("Enable all")


def disable_all(modeladmin, request, queryset):
    queryset.update(enable=False)


disable_all.short_description = gettext("Disable all")


# Register your models here.
@admin.register(HealthCheckRule)
class HealthCheckRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'http_method', 'url', 'enable', 'description')
    search_fields = ['id', 'name', 'description']
    list_filter = ('http_method', 'enable')
    actions = [enable_all, disable_all]


@admin.register(HealthCheckRecord)
class HealthCheckRecordAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "timestamp", "response_code", "request", "response_body", "response_delay",
                       "health_check_rule", "success", "error"]
    fields = (
        'id', 'health_check_rule', "request", ('response_code', 'response_body'), 'response_delay', 'success',
        'timestamp',
        'error', 'error_description')
    list_display = ('id', 'health_check_rule', 'response_code', 'response_delay', 'success', 'timestamp')
    search_fields = ['id', 'health_check_rule__name', 'response_body', 'request', 'response_code', 'error_description']
    list_filter = ('health_check_rule', 'response_code', 'success')


@admin.register(ClientCertificate)
class ClientCertificateAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Header)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
