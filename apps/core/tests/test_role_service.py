import pytest

from apps.core.models import CustomUser, Membership, Permission, Role, RolePermission, Tenant
from apps.core.services import role as role_service
from apps.core.services import permission as permission_service


@pytest.mark.django_db
class TestRoleServiceCRUD:
    def test_create_role(self):
        tenant = Tenant.objects.create(slug='test-role', name='Test Role')
        role = role_service.RoleService.create_role(tenant=tenant, name='supervisor', description='Supervisor de piso')
        assert role.name == 'supervisor'
        assert role.description == 'Supervisor de piso'
        assert role.tenant == tenant

    def test_create_duplicate_role_fails(self):
        tenant = Tenant.objects.create(slug='dup-role', name='Dup Role')
        role_service.RoleService.create_role(tenant=tenant, name='admin')
        with pytest.raises(role_service.RoleServiceError):
            role_service.RoleService.create_role(tenant=tenant, name='admin')

    def test_update_role(self):
        tenant = Tenant.objects.create(slug='upd-role', name='Upd Role')
        role = Role.objects.create(tenant=tenant, name='old_name')
        updated = role_service.RoleService.update_role(role=role, name='new_name')
        assert updated.name == 'new_name'

    def test_delete_role_without_users(self):
        tenant = Tenant.objects.create(slug='del-role', name='Del Role')
        role = Role.objects.create(tenant=tenant, name='to_delete')
        role_service.RoleService.delete_role(role=role)
        assert Role.objects.filter(pk=role.pk).first() is None

    def test_delete_role_with_users_fails(self):
        tenant = Tenant.objects.create(slug='del-fail', name='Del Fail')
        role = Role.objects.create(tenant=tenant, name='with_users')
        user = CustomUser.objects.create_user(email='user@test.com', password='test123')
        Membership.objects.create(user=user, tenant=tenant, role=role)

        with pytest.raises(role_service.RoleServiceError):
            role_service.RoleService.delete_role(role=role)


@pytest.mark.django_db
class TestRoleServicePermissions:
    def test_add_permission(self):
        tenant = Tenant.objects.create(slug='add-perm', name='Add Perm')
        role = Role.objects.create(tenant=tenant, name='test_role')
        rp = role_service.RoleService.add_permission(role=role, permission_codename='manage_inventory')
        assert rp.active is True
        assert rp.permission.codename == 'manage_inventory'

    def test_add_inactive_permission(self):
        tenant = Tenant.objects.create(slug='add-inact', name='Add Inact')
        role = Role.objects.create(tenant=tenant, name='test_role')
        rp = role_service.RoleService.add_permission(role=role, permission_codename='manage_inventory', active=False)
        assert rp.active is False

    def test_remove_permission(self):
        tenant = Tenant.objects.create(slug='rem-perm', name='Rem Perm')
        role = Role.objects.create(tenant=tenant, name='test_role')
        perm = Permission.objects.create(codename='temp_perm')
        RolePermission.objects.create(role=role, permission=perm)

        role_service.RoleService.remove_permission(role=role, permission_codename='temp_perm')
        assert RolePermission.objects.filter(role=role, permission=perm).first() is None

    def test_toggle_permission(self):
        tenant = Tenant.objects.create(slug='tog-perm', name='Tog Perm')
        role = Role.objects.create(tenant=tenant, name='test_role')
        perm = Permission.objects.create(codename='toggle_perm')
        rp = RolePermission.objects.create(role=role, permission=perm, active=True)

        new_state = role_service.RoleService.toggle_permission(role=role, permission_codename='toggle_perm')
        assert new_state is False
        rp.refresh_from_db()
        assert rp.active is False

    def test_deactivate_permission(self):
        tenant = Tenant.objects.create(slug='deact-perm', name='Deact Perm')
        role = Role.objects.create(tenant=tenant, name='test_role')
        perm = Permission.objects.create(codename='deact_perm')
        RolePermission.objects.create(role=role, permission=perm, active=True)

        rp = role_service.RoleService.deactivate_permission(role=role, permission_codename='deact_perm')
        assert rp.active is False

    def test_activate_permission(self):
        tenant = Tenant.objects.create(slug='act-perm', name='Act Perm')
        role = Role.objects.create(tenant=tenant, name='test_role')
        perm = Permission.objects.create(codename='act_perm')
        RolePermission.objects.create(role=role, permission=perm, active=False)

        rp = role_service.RoleService.activate_permission(role=role, permission_codename='act_perm')
        assert rp.active is True


@pytest.mark.django_db
class TestRoleServiceGetters:
    def test_get_permissions_all(self):
        tenant = Tenant.objects.create(slug='get-perm', name='Get Perm')
        role = Role.objects.create(tenant=tenant, name='test_role')
        p1 = Permission.objects.create(codename='perm1')
        p2 = Permission.objects.create(codename='perm2')
        RolePermission.objects.create(role=role, permission=p1, active=True)
        RolePermission.objects.create(role=role, permission=p2, active=False)

        perms = role_service.RoleService.get_permissions(role=role, active_only=False)
        assert len(perms) == 2

    def test_get_active_permissions(self):
        tenant = Tenant.objects.create(slug='get-act', name='Get Act')
        role = Role.objects.create(tenant=tenant, name='test_role')
        p1 = Permission.objects.create(codename='perm_active')
        p2 = Permission.objects.create(codename='perm_inactive')
        RolePermission.objects.create(role=role, permission=p1, active=True)
        RolePermission.objects.create(role=role, permission=p2, active=False)

        active = role_service.RoleService.get_active_permissions(role=role)
        assert len(active) == 1
        assert active[0].codename == 'perm_active'

    def test_get_inactive_permissions(self):
        tenant = Tenant.objects.create(slug='get-inact', name='Get Inact')
        role = Role.objects.create(tenant=tenant, name='test_role')
        p1 = Permission.objects.create(codename='perm_active')
        p2 = Permission.objects.create(codename='perm_inactive')
        RolePermission.objects.create(role=role, permission=p1, active=True)
        RolePermission.objects.create(role=role, permission=p2, active=False)

        inactive = role_service.RoleService.get_inactive_permissions(role=role)
        assert len(inactive) == 1
        assert inactive[0].codename == 'perm_inactive'

    def test_has_permission_active_only(self):
        tenant = Tenant.objects.create(slug='has-perm', name='Has Perm')
        role = Role.objects.create(tenant=tenant, name='test_role')
        perm = Permission.objects.create(codename='has_perm')
        RolePermission.objects.create(role=role, permission=perm, active=False)

        assert role_service.RoleService.has_permission(role=role, permission_codename='has_perm', active_only=True) is False
        assert role_service.RoleService.has_permission(role=role, permission_codename='has_perm', active_only=False) is True


@pytest.mark.django_db
class TestPermissionService:
    def test_list_all(self):
        Permission.objects.create(codename='perm_a')
        Permission.objects.create(codename='perm_b')
        perms = permission_service.PermissionService.list_all()
        assert perms.count() >= 2

    def test_get_or_create(self):
        perm, created = permission_service.PermissionService.get_or_create(codename='new_perm', description='Nuevo permiso')
        assert perm.codename == 'new_perm'
        assert created is True

        perm2, created2 = permission_service.PermissionService.get_or_create(codename='new_perm')
        assert perm2.pk == perm.pk
        assert created2 is False