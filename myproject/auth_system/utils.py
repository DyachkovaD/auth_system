from .models import User, AccessRule, BusinessElement, UserRole


def check_permission(user, element_name, action):
    """
    Проверяет наличие у пользователя прав на выполнение действия с элементом.

    Args:
        user (User): Пользователь для проверки прав
        element_name (str): Название бизнес-элемента
        action (str): Действие (read, create, update, delete, etc.)
    Returns:
        bool: True если есть права, иначе False
    """

    try:
        element = BusinessElement.objects.get(name=element_name)
    except BusinessElement.DoesNotExist:
        return False

    # Получаем все роли пользователя
    user_roles = UserRole.objects.filter(user=user).select_related('role')

    # Проверяем права для каждой роли пользователя
    for user_role in user_roles:
        try:
            access_rule = AccessRule.objects.get(role=user_role.role, element=element)

            # Проверяем конкретное разрешение в зависимости от действия
            if action == 'read' and access_rule.read_permission:
                return True
            elif action == 'read_all' and access_rule.read_all_permission:
                return True
            elif action == 'create' and access_rule.create_permission:
                return True
            elif action == 'update' and access_rule.update_permission:
                return True
            elif action == 'update_all' and access_rule.update_all_permission:
                return True
            elif action == 'delete' and access_rule.delete_permission:
                return True
            elif action == 'delete_all' and access_rule.delete_all_permission:
                return True

        except AccessRule.DoesNotExist:
            # Для данной роли нет правил доступа к элементу
            continue

    return False