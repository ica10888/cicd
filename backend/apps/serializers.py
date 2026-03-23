import hashlib
from rest_framework import serializers
from .models import AppInfo, UserInfo, RoleInfo, AppPermission


class AppInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppInfo
        fields = ['id', 'name', 'description', 'version', 'status', 'repo_url',
                  'create_time', 'update_time']


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['id', 'username', 'email', 'role', 'is_active', 'create_time', 'update_time']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['username', 'password', 'email', 'role', 'is_active']

    def create(self, validated_data):
        pwd = validated_data.get('password', '')
        validated_data['password'] = hashlib.md5(pwd.encode()).hexdigest()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = hashlib.md5(validated_data['password'].encode()).hexdigest()
        return super().update(instance, validated_data)


class RoleInfoSerializer(serializers.ModelSerializer):
    role_type_display = serializers.CharField(source='get_role_type_display', read_only=True)

    class Meta:
        model = RoleInfo
        fields = ['id', 'name', 'role_type', 'role_type_display', 'description',
                  'create_time', 'update_time']


class AppPermissionSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    app_name = serializers.SerializerMethodField()

    class Meta:
        model = AppPermission
        fields = ['id', 'role', 'role_name', 'app', 'app_name',
                  'can_create', 'can_read', 'can_update', 'can_delete',
                  'create_time', 'update_time']

    def get_app_name(self, obj):
        return obj.app.name if obj.app else '所有应用'
