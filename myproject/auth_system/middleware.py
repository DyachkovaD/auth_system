from django.http import JsonResponse
from .models import Session
import jwt
from django.conf import settings


class AuthenticationMiddleware:
    """
    Middleware для аутентификации пользователей по JWT токенам.
    Проверяет заголовок Authorization и устанавливает request.user.
    """

    def __init__(self, get_response):
        """
        Инициализация middleware.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Обрабатывает каждый входящий запрос.

        Args: request: HTTP запрос
        Returns: HttpResponse: HTTP ответ
        """
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Ищем активную сессию с данным токеном
                session = Session.objects.select_related('user').get(token=token, is_active=True)
                if session.is_valid():
                    # Устанавливаем пользователя в request
                    request.user = session.user
                    request.session_obj = session
                else:
                    # Деактивируем просроченную сессию
                    session.is_active = False
                    session.save()
                    request.user = None
            except (Session.DoesNotExist, jwt.InvalidTokenError):
                # Невалидный токен или сессия не найдена
                request.user = None
        else:
            # Заголовок Authorization отсутствует или неверного формата
            request.user = None

        response = self.get_response(request)
        return response