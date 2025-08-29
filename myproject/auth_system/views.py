from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import User, Session, Role, BusinessElement, AccessRule, UserRole
from .serializers import (
    UserRegistrationSerializer, UserSerializer, LoginSerializer,
    RoleSerializer, BusinessElementSerializer, AccessRuleSerializer,
    UserRoleSerializer
)
from .utils import check_permission


@api_view(['POST'])
def register(request):
    """
    Регистрация нового пользователя.

    POST /api/register/
    Body: {email, first_name, last_name, middle_name, password, password_confirm}
    Returns: Сообщение об успешной регистрации или ошибки валидации
    """

    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'Пользователь успешно зарегистрирован'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    """
    Аутентификация пользователя.

    POST /api/login/
    Body: {email, password}
    Returns: Response: JWT токен и данные пользователя или ошибка аутентификации
    """

    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email, is_active=True)
            if user.check_password(password):
                token = user.generate_token()
                expires_at = timezone.now() + timedelta(days=1)

                # Деактивируем предыдущие сессии пользователя
                Session.objects.filter(user=user, is_active=True).update(is_active=False)

                # Создаем новую сессию
                session = Session.objects.create(
                    user=user,
                    token=token,
                    expires_at=expires_at
                )

                return Response({
                    'token': token,
                    'user': UserSerializer(user).data
                })
            else:
                return Response({'error': 'Неверный пароль'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout(request):
    """
    Выход из системы.

    POST /api/logout/
    Headers: Authorization: Bearer {token}
    Returns: Response: Сообщение об успешном выходе или ошибка
    """

    if hasattr(request, 'session_obj'):
        request.session_obj.is_active = False
        request.session_obj.save()
        return Response({'message': 'Успешный выход из системы'})
    return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT'])
def profile(request):
    """
    Получение и обновление профиля пользователя.

    GET /api/profile/ - получение профиля
    PUT /api/profile/ - обновление профиля
    Headers: Authorization: Bearer {token}

    Returns:Response: Данные пользователя или ошибки
    """
    if not request.user or not request.user.is_authenticated:
        return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_account(request):
    """
    Мягкое удаление аккаунта пользователя.

    DELETE /api/delete-account/
    Headers: Authorization: Bearer {token}

    Returns: Response: Сообщение об успешном удалении
    """
    if not request.user or not request.user.is_authenticated:
        return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

    # Мягкое удаление - устанавливаем is_active=False
    request.user.is_active = False
    request.user.deleted_at = timezone.now()
    request.user.save()

    # Деактивируем текущую сессию
    if hasattr(request, 'session_obj'):
        request.session_obj.is_active = False
        request.session_obj.save()

    return Response({'message': 'Аккаунт успешно удален'})


@api_view(['GET', 'POST'])
def role_list(request):
    """
    Получение списка ролей и создание новой роли (только для админов).

    GET /api/admin/roles/ - список всех ролей
    POST /api/admin/roles/ - создание новой роли
    Headers: Authorization: Bearer {token}

    Returns: Response: Список ролей или созданная роль
    """

    if not request.user or not request.user.is_authenticated:
        return Response({'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)

    # Проверяем права доступа к управлению правилами доступа
    if not check_permission(request.user, 'access_rules', 'read'):
        return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Дополнительная проверка на право создания
        if not check_permission(request.user, 'access_rules', 'create'):
            return Response({'error': 'Доступ запрещен'}, status=status.HTTP_403_FORBIDDEN)

        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)