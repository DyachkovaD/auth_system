from rest_framework import serializers
from .models import User, Role, BusinessElement, AccessRule, UserRole


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации новых пользователей.
    Включает проверку подтверждения пароля.
    """

    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'middle_name', 'password', 'password_confirm']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """
        Проверяет совпадение пароля и подтверждения пароля.

        Args: data (dict): Данные для валидации
        """

        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        """
        Создает нового пользователя.

        Args: validated_data (dict): Валидированные данные
        Returns: User: Созданный пользователь
        """
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о пользователе."""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'middle_name', 'is_active']
        read_only_fields = ['id', 'is_active']


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа в систему.
    Проверяет email и пароль.
    """

    email = serializers.EmailField()
    password = serializers.CharField()


class RoleSerializer(serializers.ModelSerializer):
    """Сериализатор для ролей пользователей."""

    class Meta:
        model = Role
        fields = '__all__'


class BusinessElementSerializer(serializers.ModelSerializer):
    """Сериализатор для бизнес-элементов системы."""

    class Meta:
        model = BusinessElement
        fields = '__all__'


class AccessRuleSerializer(serializers.ModelSerializer):
    """Сериализатор для правил доступа."""

    class Meta:
        model = AccessRule
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    """Сериализатор для связи пользователей с ролями."""

    class Meta:
        model = UserRole
        fields = '__all__'