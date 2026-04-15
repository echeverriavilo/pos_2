from django.db import transaction

from apps.core.models import Permission


class PermissionService:
    @classmethod
    def list_all(cls):
        """Lista todos los permisos del sistema.

        Retorna:
        - QuerySet de Permission.
        """
        return Permission.objects.all()

    @classmethod
    def get_or_create(cls, *, codename: str, description: str = '') -> tuple[Permission, bool]:
        """Crea o obtiene un permiso.

        Parámetros:
        - codename: identificador único del permiso.
        - description: descripción opcional.

        Retorna:
        - Tupla (Permission, created).
        """
        defaults = {'description': description} if description else {}
        return Permission.objects.get_or_create(codename=codename, defaults=defaults)

    @classmethod
    def create(cls, *, codename: str, description: str = '') -> Permission:
        """Crea un nuevo permiso.

        Parámetros:
        - codename: identificador único.
        - description: descripción opcional.

        Retorna:
        - Permission creado.
        """
        return Permission.objects.create(codename=codename, description=description)

    @classmethod
    def get_by_codename(cls, codename: str):
        """Obtiene un permiso por codename.

        Parámetros:
        - codename: identificador del permiso.

        Retorna:
        - Permission o None.
        """
        return Permission.objects.filter(codename=codename).first()