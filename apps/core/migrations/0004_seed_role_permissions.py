from django.db import migrations


ROLE_PERMISSIONS = {
    'administrador': [
        'create_order',
        'add_item',
        'remove_item',
        'register_payment',
        'manage_inventory',
        'manage_users',
        'manage_tables',
    ],
    'cajero': [
        'register_payment',
    ],
    'garzón': [
        'create_order',
        'add_item',
        'remove_item',
        'manage_tables',
    ],
}


def seed_role_permissions(apps, schema_editor):
    Permission = apps.get_model('core', 'Permission')
    Role = apps.get_model('core', 'Role')
    RolePermission = apps.get_model('core', 'RolePermission')
    db_alias = schema_editor.connection.alias

    for role in Role.objects.using(db_alias).all():
        perms = ROLE_PERMISSIONS.get(role.name, [])
        for perm_codename in perms:
            try:
                perm = Permission.objects.using(db_alias).get(codename=perm_codename)
            except Permission.DoesNotExist:
                perm = Permission.objects.using(db_alias).create(
                    codename=perm_codename,
                    description=f'Permiso para {perm_codename}'
                )
            RolePermission.objects.using(db_alias).get_or_create(
                role=role,
                permission=perm,
            )


def reverse_seed_role_permissions(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_permissions_data'),
    ]

    operations = [
        migrations.RunPython(seed_role_permissions, reverse_seed_role_permissions),
    ]