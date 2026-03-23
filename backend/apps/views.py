import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import AppInfo, UserInfo, RoleInfo, AppPermission
from .serializers import (AppInfoSerializer, UserInfoSerializer, UserCreateSerializer,
                          RoleInfoSerializer, AppPermissionSerializer)


def success(data=None, msg='success'):
    return Response({'code': 200, 'msg': msg, 'data': data})


def error(msg='error', code=400):
    return Response({'code': code, 'msg': msg, 'data': None}, status=status.HTTP_200_OK)


# ─── Application CRUD ────────────────────────────────────────────────────────

class AppListView(APIView):
    def get(self, request):
        apps = AppInfo.objects.filter(deleted=False).order_by('-create_time')
        return success(AppInfoSerializer(apps, many=True).data)

    def post(self, request):
        ser = AppInfoSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '创建成功')
        return error(str(ser.errors))


class AppDetailView(APIView):
    def _get_obj(self, pk):
        try:
            return AppInfo.objects.get(pk=pk, deleted=False)
        except AppInfo.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('应用不存在', 404)
        return success(AppInfoSerializer(obj).data)

    def put(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('应用不存在', 404)
        ser = AppInfoSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '更新成功')
        return error(str(ser.errors))

    def delete(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('应用不存在', 404)
        obj.deleted = True
        obj.save(update_fields=['deleted', 'update_time'])
        return success(msg='删除成功')


# ─── Role CRUD ───────────────────────────────────────────────────────────────

class RoleListView(APIView):
    def get(self, request):
        roles = RoleInfo.objects.filter(deleted=False).order_by('-create_time')
        return success(RoleInfoSerializer(roles, many=True).data)

    def post(self, request):
        ser = RoleInfoSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '创建成功')
        return error(str(ser.errors))


class RoleDetailView(APIView):
    def _get_obj(self, pk):
        try:
            return RoleInfo.objects.get(pk=pk, deleted=False)
        except RoleInfo.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('角色不存在', 404)
        return success(RoleInfoSerializer(obj).data)

    def put(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('角色不存在', 404)
        ser = RoleInfoSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '更新成功')
        return error(str(ser.errors))

    def delete(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('角色不存在', 404)
        obj.deleted = True
        obj.save(update_fields=['deleted', 'update_time'])
        return success(msg='删除成功')


# ─── AppPermission CRUD ───────────────────────────────────────────────────────

class AppPermissionListView(APIView):
    def get(self, request):
        qs = AppPermission.objects.filter(deleted=False).select_related('role', 'app')
        role_id = request.query_params.get('role_id')
        if role_id:
            qs = qs.filter(role_id=role_id)
        return success(AppPermissionSerializer(qs, many=True).data)

    def post(self, request):
        ser = AppPermissionSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '创建成功')
        return error(str(ser.errors))


class AppPermissionDetailView(APIView):
    def _get_obj(self, pk):
        try:
            return AppPermission.objects.get(pk=pk, deleted=False)
        except AppPermission.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('权限配置不存在', 404)
        return success(AppPermissionSerializer(obj).data)

    def put(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('权限配置不存在', 404)
        ser = AppPermissionSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '更新成功')
        return error(str(ser.errors))

    def delete(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('权限配置不存在', 404)
        obj.deleted = True
        obj.save(update_fields=['deleted', 'update_time'])
        return success(msg='删除成功')


# ─── Login ───────────────────────────────────────────────────────────────────

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        role = request.data.get('role', 'user')

        if not username or not password:
            return error('用户名和密码不能为空')

        hashed = hashlib.md5(password.encode()).hexdigest()
        try:
            user = UserInfo.objects.get(username=username, password=hashed,
                                        is_active=True, deleted=False)
        except UserInfo.DoesNotExist:
            return error('用户名或密码错误', 401)

        if role == 'admin' and user.role != 'admin':
            return error('无管理员权限', 403)

        return success({'id': user.id, 'username': user.username,
                        'role': user.role, 'email': user.email}, '登录成功')

class UserListView(APIView):
    def get(self, request):
        users = UserInfo.objects.filter(deleted=False).order_by('-create_time')
        return success(UserInfoSerializer(users, many=True).data)

    def post(self, request):
        ser = UserCreateSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return success(UserInfoSerializer(ser.instance).data, '创建成功')
        return error(str(ser.errors))


class UserDetailView(APIView):
    def _get_obj(self, pk):
        try:
            return UserInfo.objects.get(pk=pk, deleted=False)
        except UserInfo.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('用户不存在', 404)
        return success(UserInfoSerializer(obj).data)

    def put(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('用户不存在', 404)
        ser = UserCreateSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return success(UserInfoSerializer(ser.instance).data, '更新成功')
        return error(str(ser.errors))

    def delete(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error('用户不存在', 404)
        obj.deleted = True
        obj.save(update_fields=['deleted', 'update_time'])
        return success(msg='删除成功')
