from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from auth_system.utils import check_permission


@api_view(['GET'])
def products_list(request):
    """
    Получение списка продуктов.

    GET /api/products/

    Returns: Response: Список продуктов или ошибка доступа
    """
    print(f"Request user: {request.user}")
    print(f"User authenticated: {request.user.is_authenticated}")
    # Проверка аутентификации пользователя
    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа на чтение продуктов
    if not check_permission(request.user, 'products', 'read'):
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Mock данные продуктов (в реальной системе здесь был бы запрос к БД)
    products = [
        {'id': 1, 'name': 'Ноутбук Lenovo', 'price': 45000, 'category': 'Электроника'},
        {'id': 2, 'name': 'Смартфон Samsung', 'price': 25000, 'category': 'Электроника'},
        {'id': 3, 'name': 'Наушники Sony', 'price': 8000, 'category': 'Аксессуары'},
    ]

    return Response(products)


@api_view(['POST'])
def create_product(request):
    """
    Создание нового продукта.

    POST /api/products/create/
    Body: {name, price, category, description}

    Returns: Response: Сообщение об успешном создании или ошибка доступа
    """

    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа на создание продуктов
    if not check_permission(request.user, 'products', 'create'):
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # В реальной системе здесь была бы валидация и сохранение в БД
    # Для примера просто возвращаем успешный ответ
    return Response(
        {'message': 'Продукт успешно создан', 'data': request.data},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def orders_list(request):
    """
    Получение списка заказов.

    GET /api/orders/

    Returns: Response: Список заказов или ошибка доступа
    """

    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа на чтение заказов
    if not check_permission(request.user, 'orders', 'read'):
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Mock данные заказов
    orders = [
        {'id': 1, 'user_id': request.user.id, 'total_amount': 53000, 'status': 'completed'},
        {'id': 2, 'user_id': request.user.id, 'total_amount': 12000, 'status': 'processing'},
    ]

    return Response(orders)


@api_view(['POST'])
def create_order(request):
    """
    Создание нового заказа.

    POST /api/orders/create/
    Body: {product_ids, quantities, shipping_address}

    Returns: Response: Сообщение об успешном создании заказа или ошибка доступа
    """

    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа на создание заказов
    if not check_permission(request.user, 'orders', 'create'):
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Mock создание заказа
    return Response(
        {'message': 'Заказ успешно создан', 'order_id': 123},
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def users_list(request):
    """
    Получение списка пользователей (только для администраторов).

    GET /api/users/

    Returns: Response: Список пользователей или ошибка доступа
    """

    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа на чтение всех пользователей
    if not check_permission(request.user, 'users', 'read_all'):
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Mock данные пользователей (в реальной системе - запрос к БД)
    users = [
        {'id': 1, 'email': 'admin@example.com', 'first_name': 'Админ', 'last_name': 'Системный'},
        {'id': 2, 'email': 'user1@example.com', 'first_name': 'Иван', 'last_name': 'Петров'},
        {'id': 3, 'email': 'user2@example.com', 'first_name': 'Мария', 'last_name': 'Сидорова'},
    ]

    return Response(users)


@api_view(['PUT'])
def update_product(request, product_id):
    """
    Обновление информации о продукте.

    PUT /api/products/{product_id}/
    Body: {name, price, category, description}

    Args: product_id (int): ID продукта для обновления
    Returns: Response: Обновленные данные продукта или ошибка доступа
    """

    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа на обновление продуктов
    has_update_all = check_permission(request.user, 'products', 'update_all')
    has_update_own = check_permission(request.user, 'products', 'update')

    if not has_update_all and not has_update_own:
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # В реальной системе здесь было бы обновление данных в БД

    return Response({
        'message': 'Продукт успешно обновлен',
        'product_id': product_id,
        'updated_data': request.data
    })


@api_view(['DELETE'])
def delete_product(request, product_id):
    """
    Удаление продукта.

    DELETE /api/products/{product_id}/

    Args: product_id (int): ID продукта для удаления
    Returns: Response: Сообщение об успешном удалении или ошибка доступа
    """

    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа на удаление продуктов
    has_delete_all = check_permission(request.user, 'products', 'delete_all')
    has_delete_own = check_permission(request.user, 'products', 'delete')

    if not has_delete_all and not has_delete_own:
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # В реальной системе здесь было бы удаление из БД

    return Response({
        'message': 'Продукт успешно удален',
        'product_id': product_id
    })


@api_view(['GET'])
def dashboard(request):
    """
    Получение данных для dashboard (статистика, сводка).

    GET /api/dashboard/

    Returns: Response: Статистические данные или ошибка доступа
    """

    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа к dashboard
    if not check_permission(request.user, 'dashboard', 'read'):
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Mock данные для dashboard
    dashboard_data = {
        'total_products': 156,
        'total_orders': 42,
        'total_users': 23,
        'revenue': 1250000,
        'recent_activity': [
            {'action': 'order_created', 'user': 'user1@example.com', 'time': '2024-01-15 10:30'},
            {'action': 'product_updated', 'user': 'admin@example.com', 'time': '2024-01-15 09:15'},
            {'action': 'user_registered', 'user': 'newuser@example.com', 'time': '2024-01-15 08:45'},
        ]
    }

    return Response(dashboard_data)


@api_view(['GET'])
def product_detail(request, product_id):
    """
    Получение детальной информации о продукте.

    GET /api/products/{product_id}/

    Args: product_id (int): ID продукта
    Returns: Response: Детальная информация о продукте или ошибка доступа
    """

    if not request.user or not request.user.is_authenticated:
        return Response(
            {'error': 'Не авторизован'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Проверка прав доступа на чтение продуктов
    if not check_permission(request.user, 'products', 'read'):
        return Response(
            {'error': 'Доступ запрещен'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Mock данные продукта
    product = {
        'id': product_id,
        'name': f'Продукт {product_id}',
        'price': 1000 * product_id,
        'category': 'Электроника',
        'description': f'Это описание продукта {product_id}',
        'created_at': '2024-01-01',
        'updated_at': '2024-01-15',
        'stock_quantity': 50,
        'rating': 4.5
    }

    return Response(product)