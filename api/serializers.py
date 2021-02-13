from django.contrib.auth.models import User
from rest_framework import serializers

from .models import GUser, GameLog, VisitLog, UserInventory, Gun, Skin
from .utils import is_valid_word, SCHOOL_EMAIL_ADDRESS


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameLog
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
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    matches = GameSerializer(many=True, read_only=True)

    class Meta:
        model = GUser
        fields = ['id', 'username', 'email', 'auth', 'level', 'inventory', 'matches']


class UserInventorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='get_displayable_id', read_only=True)
    main_guns = serializers.ListField(source='get_main_guns_dict', read_only=True)
    side_guns = serializers.ListField(source='get_side_guns_dict', read_only=True)
    skins = serializers.ListField(source='get_skins_dict', read_only=True)
    abilities = serializers.ListField(source='get_abilities_dict', read_only=True)

    class Meta:
        model = UserInventory
        fields = '__all__'


class DisplayUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    inventory = UserInventorySerializer(read_only=True)

    class Meta:
        model = GUser
        fields = ['id', 'username', 'email', 'level', 'balance', 'inventory']


class ScoreboardUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = GUser
        fields = ['username', 'score']

class VisitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitLog
        fields = '__all__'


class GunSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='get_displayable_id')

    class Meta:
        model = Gun
        fields = '__all__'


class SkinSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='get_displayable_id')

    class Meta:
        model = Skin
        fields = '__all__'