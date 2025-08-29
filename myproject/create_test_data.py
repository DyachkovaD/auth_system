import os
import django
import sys

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from auth_system.models import User, Role, BusinessElement, AccessRule, UserRole
from django.contrib.auth import get_user_model


def create_test_data():
    print("Создание тестовых данных...")

    # Создаем роли
    admin_role, created = Role.objects.get_or_create(
        name='admin',
        defaults={'description': 'Администратор системы'}
    )

    user_role, created = Role.objects.get_or_create(
        name='user',
        defaults={'description': 'Обычный пользователь'}
    )

    # Создаем бизнес-элементы
    elements_data = [
        ('products', 'Управление товарами'),
        ('orders', 'Управление заказами'),
        ('users', 'Управление пользователями'),
        ('access_rules', 'Управление правами доступа'),
        ('dashboard', 'Панель управления'),
    ]

    elements = {}
    for name, description in elements_data:
        element, created = BusinessElement.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        elements[name] = element

    # Создаем правила доступа для админа
    for element in elements.values():
        AccessRule.objects.get_or_create(
            role=admin_role,
            element=element,
            defaults={
                'read_permission': True,
                'read_all_permission': True,
                'create_permission': True,
                'update_permission': True,
                'update_all_permission': True,
                'delete_permission': True,
                'delete_all_permission': True,
            }
        )

    # Создаем правила доступа для обычного пользователя
    AccessRule.objects.get_or_create(
        role=user_role,
        element=elements['products'],
        defaults={
            'read_permission': True,
            'create_permission': True,
            'update_permission': True,
            'delete_permission': True,
        }
    )

    AccessRule.objects.get_or_create(
        role=user_role,
        element=elements['orders'],
        defaults={
            'read_permission': True,
            'create_permission': True,
        }
    )

    # Создаем пользователей
    User = get_user_model()

    admin_user, created = User.objects.get_or_create(
        email='admin@example.com',
        defaults={
            'first_name': 'Админ',
            'last_name': 'Системный',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()

    regular_user, created = User.objects.get_or_create(
        email='user@example.com',
        defaults={
            'first_name': 'Иван',
            'last_name': 'Петров'
        }
    )
    if created:
        regular_user.set_password('user123')
        regular_user.save()

    # Назначаем роли
    UserRole.objects.get_or_create(user=admin_user, role=admin_role)
    UserRole.objects.get_or_create(user=regular_user, role=user_role)

    print("Тестовые данные созданы успешно!")
    print("Админ: admin@example.com / admin123")
    print("Пользователь: user@example.com / user123")


if __name__ == '__main__':
    create_test_data()