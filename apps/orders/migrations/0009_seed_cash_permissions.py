from django.db import migrations


def seed_cash_permissions(apps, schema_editor):
    Permission = apps.get_model('core', 'Permission')
    Role = apps.get_model('core', 'Role')
    RolePermission = apps.get_model('core', 'RolePermission')

    cash_permissions = [
        ('manage_cash_registers', 'Gestionar cajas registradoras'),
        ('open_cash_session', 'Abrir sesiones de caja'),
        ('close_cash_session', 'Cerrar sesiones de caja'),
    ]

    for codename, description in cash_permissions:
        Permission.objects.get_or_create(
            codename=codename,
            defaults={'description': description},
        )

    for role in Role.objects.all():
        if role.name == 'administrador':
            for codename, _ in cash_permissions:
                perm = Permission.objects.get(codename=codename)
                RolePermission.objects.get_or_create(
                    role=role,
                    permission=perm,
                    defaults={'active': True},
                )
        elif role.name in ('cajero', 'caja'):
            for codename in ('open_cash_session', 'close_cash_session'):
                perm = Permission.objects.get(codename=codename)
                RolePermission.objects.get_or_create(
                    role=role,
                    permission=perm,
                    defaults={'active': True},
                )


def rollback_cash_permissions(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_cashregister_cashsession_cashmovement'),
        ('core', '0005_rolepermission_active_rolepermission_updated_at_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_cash_permissions, rollback_cash_permissions),
    ]