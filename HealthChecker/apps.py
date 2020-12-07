from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.models import Q
import os


def my_callback(sender, **kwargs):
    from django.contrib.auth.models import User, Group, Permission
    members, created = Group.objects.get_or_create(name='members')
    if not created:
        return
    permissions = Permission.objects.all().exclude(codename__in=['delete_permission',
                                                                 'change_permission', 'add_permission','view_permission', 'add_group',
                                                                 'change_group', 'delete_group', 'add_user', 'delete_user'
                                                                 'change_user', 'add_contenttype', 'change_contenttype',
                                                                 'delete_contenttype', 'add_logentry', 'change_logentry',
                                                                 'delete_logentry', 'add_session', 'change_session',
                                                                 'delete_session', 'view_group', 'view_user', ])
    permissions = permissions.filter(~Q(codename = 'delete_user') & ~Q(codename = 'change_user'))
    members.permissions.add(*permissions)
    admins = Group.objects.create(name='admins')
    admins_permissions = Permission.objects.all()
    admins.permissions.add(*admins_permissions)

    User.objects.create_superuser(os.environ.get('AWT_ADMIN', 'admin'), os.environ.get('AWT_PASS', 'admin'))

class HealthCheckerConfig(AppConfig):
    name = 'HealthChecker'

    def ready(self):
        post_migrate.connect(my_callback, sender=self)