from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import bcrypt
import jwt
from datetime import datetime, timedelta
from django.conf import settings


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели User с поддержкой bcrypt хеширования паролей"""

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с указанным email и паролем.

        Args:
            email (str): Email пользователя
            password (str): Пароль пользователя
            **extra_fields: Дополнительные поля пользователя
        Returns:
            User: Созданный пользователь
        """
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет суперпользователя.

        Args:
            email (str): Email суперпользователя
            password (str): Пароль суперпользователя
            **extra_fields: Дополнительные поля
        Returns:
            User: Созданный суперпользователь
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    """
    Кастомная модель пользователя с поддержкой bcrypt хеширования паролей
    и JWT токенов для аутентификации.
    """

    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    middle_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Отчество')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    is_staff = models.BooleanField(default=False, verbose_name='Персонал')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперпользователь')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def set_password(self, raw_password):
        """
        Хеширует пароль с использованием bcrypt.

        Args: raw_password (str): Исходный пароль
        """
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, raw_password):
        """
        Проверяет соответствие пароля хешу в базе данных.

        Args: raw_password (str): Пароль для проверки
        Returns: bool: True если пароль верный, иначе False
        """
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def generate_token(self):
        """
        Генерирует JWT токен для пользователя.

        Returns: str: JWT токен
        """
        payload = {
            'user_id': self.id,
            'exp': datetime.now() + timedelta(days=1),  # Токен действителен 1 день
            'iat': datetime.now()  # Время создания токена
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    def __str__(self):
        return f"{self.email} ({self.first_name} {self.last_name})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Role(models.Model):
    """
    Модель ролей пользователей в системе.
    Определяет группы пользователей с общими правами доступа.
    """

    name = models.CharField(max_length=50, unique=True, verbose_name='Название роли')
    description = models.TextField(blank=True, verbose_name='Описание роли')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class BusinessElement(models.Model):
    """
    Модель бизнес-элементов системы.
    Представляет объекты, к которым можно настраивать доступ.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name='Название элемента')
    description = models.TextField(blank=True, verbose_name='Описание элемента')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'


class AccessRule(models.Model):
    """
    Модель правил доступа.
    Связывает роли с бизнес-элементами и определяет разрешения.
    """

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='access_rules', verbose_name='Роль')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='access_rules',
                                verbose_name='Элемент')
    # Права доступа
    read_permission = models.BooleanField(default=False, verbose_name='Чтение своих')
    read_all_permission = models.BooleanField(default=False, verbose_name='Чтение всех')
    create_permission = models.BooleanField(default=False, verbose_name='Создание')
    update_permission = models.BooleanField(default=False, verbose_name='Обновление своих')
    update_all_permission = models.BooleanField(default=False, verbose_name='Обновление всех')
    delete_permission = models.BooleanField(default=False, verbose_name='Удаление своих')
    delete_all_permission = models.BooleanField(default=False, verbose_name='Удаление всех')

    class Meta:
        unique_together = ['role', 'element']
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'

    def __str__(self):
        return f"{self.role.name} -> {self.element.name}"


class UserRole(models.Model):
    """
    Модель связи пользователей с ролями.
    Пользователь может иметь несколько ролей.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles', verbose_name='Пользователь')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles', verbose_name='Роль')

    class Meta:
        unique_together = ['user', 'role']
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class Session(models.Model):
    """
    Модель сессий пользователей.
    Хранит активные JWT токены для управления сессиями.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name='Пользователь')
    token = models.CharField(max_length=500, unique=True, verbose_name='JWT токен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    expires_at = models.DateTimeField(verbose_name='Дата истечения')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    def is_valid(self):
        """
        Проверяет валидность сессии.

        Returns: True если сессия активна и не истекла, иначе False
        """
        return self.is_active and datetime.now() < self.expires_at

    def __str__(self):
        return f"Session for {self.user.email}"

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'