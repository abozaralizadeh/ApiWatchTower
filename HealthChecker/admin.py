from django.contrib import admin
from .models import *
from django.utils.translation import gettext
from django.conf import settings
import redis


r = redis.Redis(host=settings.AWT_REDIS_HOST, port=settings.AWT_REDIS_PORT, db=1, decode_responses=True)


def enable_all(modeladmin, request, queryset):
    queryset.update(enable=True)


enable_all.short_description = gettext("Enable")


def disable_all(modeladmin, request, queryset):
    queryset.update(enable=False)


disable_all.short_description = gettext("Disable")


def duplicate_all(modeladmin, request, queryset):
    for obj in queryset:
        obj.name = "Copy of " + obj.name
        obj.id = None
        obj.save()


duplicate_all.short_description = gettext("Duplicate")


# Register your models here.
@admin.register(HealthCheckRule)
class HealthCheckRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'http_method', 'url', 'enable', 'description')
    search_fields = ['id', 'name', 'description']
    list_filter = ('http_method', 'enable')
    actions = [enable_all, disable_all, duplicate_all]


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


@admin.register(EnvironmentVariable)
class EnvironmentVariablesAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            r.delete(obj.key)
        super(EnvironmentVariablesAdmin, self).delete_queryset(request, queryset)