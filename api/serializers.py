from django.contrib.auth.models import User
from rest_framework import serializers

from .models import GUser, Game, Visitor
from .utils import is_valid_word, SCHOOL_EMAIL_ADDRESS


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(min_length=8, max_length=128, required=True)
    rpassword = serializers.CharField(min_length=8, max_length=128, required=True)

    def validate_username(self, value):
        # Check if username has swears or spaces
        if not is_valid_word(value) or (' ' in value):
            raise serializers.ValidationError('Username non valido')

        # Check if username already exists
        if GUser.objects.filter(user__username=value).exists():
            raise serializers.ValidationError('Username già in uso')

        return value

    def validate_email(self, value):
        # Chck if email is school-owned
        if not value.endswith(SCHOOL_EMAIL_ADDRESS):
            raise serializers.ValidationError('Devi usare la mail scolastica')

        # Check if email already exists on database
        if GUser.objects.filter(user__email=value).exists():
            raise serializers.ValidationError('Questa email è già stata usata')

        return value

    def validate(self, data):
        """
        Validate input data
        """

        if data['password'] != data['rpassword']:
            raise serializers.ValidationError(detail='Password non uguali', code='password')

        return data


class UserSerializer(serializers.ModelSerializer):
    games = GameSerializer(many=True, read_only=True)
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = GUser
        fields = ['id', 'username', 'email', 'auth', 'score', 'games']


class DisplayUserSeializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = GUser
        fields = ['id', 'username', 'email', 'score']


class ScoreboardUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = GUser
        fields = ['username', 'score']

class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = '__all__'


