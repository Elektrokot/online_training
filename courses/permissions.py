from rest_framework.permissions import BasePermission


class IsModeratorOrReadOnly(BasePermission):
    """
    Разрешает чтение и обновление только модераторам.
    """

    def has_permission(self, request, view):
        # Если пользователь не авторизован, доступ запрещён
        if not request.user.is_authenticated:
            return False

        # Если это безопасный метод (GET, HEAD, OPTIONS), разрешаем
        if request.method in ["GET"]:
            return True

        # Проверяем, состоит ли пользователь в группе "Модераторы"
        if request.user.groups.filter(name="Модераторы").exists():
            return True

        # Остальным пользователям (не модераторам) запрещаем
        return False


class IsOwner(BasePermission):
    """
    Разрешает доступ только владельцу объекта.
    """

    def has_object_permission(self, request, view, obj):
        # Предполагаем, что у объекта есть поле owner
        return obj.owner == request.user
