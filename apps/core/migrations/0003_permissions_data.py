from django.db import migrations


PERMISSIONS_DATA = [
    ('create_order', 'Crear órdenes'),
    ('add_item', 'Agregar productos a una orden'),
    ('remove_item', 'Anular productos de una orden'),
    ('register_payment', 'Registrar pagos'),
    ('manage_inventory', 'Gestionar inventario'),
    ('manage_users', 'Gestionar usuarios del tenant'),
    ('manage_tables', 'Gestionar mesas'),
]


def create_permissions(apps, schema_editor):
    Permission = apps.get_model('core', 'Permission')
    db_alias = schema_editor.connection.alias
    for codename, description in PERMISSIONS_DATA:
        Permission.objects.using(db_alias).get_or_create(
            codename=codename,
            defaults={'description': description}
        )


def reverse_permissions(apps, schema_editor):
    Permission = apps.get_model('core', 'Permission')
    db_alias = schema_editor.connection.alias
    Permission.objects.using(db_alias).filter(
        codename__in=[c for c, _ in PERMISSIONS_DATA]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_permission_rolepermission_role_permissions'),
    ]

    operations = [
        migrations.RunPython(create_permissions, reverse_permissions),
    ]