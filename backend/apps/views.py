import hashlib
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import AppInfo, UserInfo, RoleInfo, AppPermission
from .serializers import (AppInfoSerializer, UserInfoSerializer, UserCreateSerializer,
                          RoleInfoSerializer, AppPermissionSerializer)


def success(data=None, msg='success'):
    return Response({'code': 200, 'msg': msg, 'data': data})


def error(msg='error', code=400):
    return Response({'code': code, 'msg': msg, 'data': None}, status=status.HTTP_200_OK)


def paginate(request, queryset, serializer_class):
    """通用分页辅助函数"""
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    data = serializer_class(page, many=True).data
    return success({
        'count': paginator.page.paginator.count,
        'next': paginator.get_next_link(),
        'previous': paginator.get_previous_link(),
        'results': data,
    })


# ─── Permission helpers ───────────────────────────────────────────────────────

def get_user_permission(user_info, app_id=None):
    """
    查询用户对指定应用的权限。
    优先级：应用级权限 > 全局权限（app=None）
    admin 用户拥有所有权限。
    """
    if user_info.role == 'admin':
        return {'can_create': True, 'can_read': True, 'can_update': True, 'can_delete': True}

    roles = RoleInfo.objects.filter(deleted=False)
    perm = None
    for role in roles:
        if app_id:
            try:
                perm = AppPermission.objects.get(role=role, app_id=app_id, deleted=False)
                break
            except AppPermission.DoesNotExist:
                pass
        try:
            perm = AppPermission.objects.get(role=role, app=None, deleted=False)
            break
        except AppPermission.DoesNotExist:
            pass

    if perm:
        return {
            'can_create': perm.can_create,
            'can_read': perm.can_read,
            'can_update': perm.can_update,
            'can_delete': perm.can_delete,
        }
    return {'can_create': False, 'can_read': True, 'can_update': False, 'can_delete': False}


def require_perm(request, action, app_id=None):
    """检查当前登录用户是否有指定操作权限，返回 None 表示通过，返回 Response 表示拒绝。"""
    try:
        user_info = UserInfo.objects.get(
            username=request.user.username, deleted=False, is_active=True
        )
    except UserInfo.DoesNotExist:
        return error('用户不存在', 403)

    perms = get_user_permission(user_info, app_id)
    if not perms.get(action):
        return error('无操作权限', 403)
    return None


# ─── Base Detail View (DRY) ───────────────────────────────────────────────────

class BaseDetailView(APIView):
    """通用详情视图基类，子类声明 model / serializer / not_found_msg。"""
    model = None
    serializer = None
    not_found_msg = '对象不存在'

    def _get_obj(self, pk):
        try:
            return self.model.objects.get(pk=pk, deleted=False)
        except self.model.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error(self.not_found_msg, 404)
        return success(self.serializer(obj).data)

    def put(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error(self.not_found_msg, 404)
        ser = self.serializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '更新成功')
        return error(str(ser.errors))

    def delete(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error(self.not_found_msg, 404)
        obj.deleted = True
        obj.save(update_fields=['deleted', 'update_time'])
        return success(msg='删除成功')


# ─── Application CRUD ────────────────────────────────────────────────────────

class AppListView(APIView):
    def get(self, request):
        denied = require_perm(request, 'can_read')
        if denied:
            return denied
        apps = AppInfo.objects.filter(deleted=False).order_by('-create_time')
        return paginate(request, apps, AppInfoSerializer)

    def post(self, request):
        denied = require_perm(request, 'can_create')
        if denied:
            return denied
        ser = AppInfoSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '创建成功')
        return error(str(ser.errors))


class AppDetailView(BaseDetailView):
    model = AppInfo
    serializer = AppInfoSerializer
    not_found_msg = '应用不存在'

    def get(self, request, pk):
        denied = require_perm(request, 'can_read', app_id=pk)
        if denied:
            return denied
        return super().get(request, pk)

    def put(self, request, pk):
        denied = require_perm(request, 'can_update', app_id=pk)
        if denied:
            return denied
        return super().put(request, pk)

    def delete(self, request, pk):
        denied = require_perm(request, 'can_delete', app_id=pk)
        if denied:
            return denied
        return super().delete(request, pk)


# ─── Role CRUD ───────────────────────────────────────────────────────────────

class RoleListView(APIView):
    def get(self, request):
        roles = RoleInfo.objects.filter(deleted=False).order_by('-create_time')
        return paginate(request, roles, RoleInfoSerializer)

    def post(self, request):
        ser = RoleInfoSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '创建成功')
        return error(str(ser.errors))


class RoleDetailView(BaseDetailView):
    model = RoleInfo
    serializer = RoleInfoSerializer
    not_found_msg = '角色不存在'


# ─── AppPermission CRUD ───────────────────────────────────────────────────────

class AppPermissionListView(APIView):
    def get(self, request):
        qs = AppPermission.objects.filter(deleted=False).select_related('role', 'app')
        role_id = request.query_params.get('role_id')
        if role_id:
            qs = qs.filter(role_id=role_id)
        return paginate(request, qs, AppPermissionSerializer)

    def post(self, request):
        ser = AppPermissionSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return success(ser.data, '创建成功')
        return error(str(ser.errors))


class AppPermissionDetailView(BaseDetailView):
    model = AppPermission
    serializer = AppPermissionSerializer
    not_found_msg = '权限配置不存在'


# ─── Login ───────────────────────────────────────────────────────────────────

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()
        role = request.data.get('role', 'user')

        if not username or not password:
            return error('用户名和密码不能为空')

        hashed = hashlib.md5(password.encode()).hexdigest()
        try:
            user_info = UserInfo.objects.get(
                username=username, password=hashed, is_active=True, deleted=False
            )
        except UserInfo.DoesNotExist:
            return error('用户名或密码错误', 401)

        if role == 'admin' and user_info.role != 'admin':
            return error('无管理员权限', 403)

        from django.contrib.auth.models import User as DjangoUser
        from django.utils import timezone
        django_user, _ = DjangoUser.objects.get_or_create(
            username=username,
            defaults={'last_login': timezone.now()}
        )
        token, _ = Token.objects.get_or_create(user=django_user)

        return success({
            'id': user_info.id,
            'username': user_info.username,
            'role': user_info.role,
            'email': user_info.email,
            'token': token.key,
        }, '登录成功')


# ─── User CRUD ───────────────────────────────────────────────────────────────

class UserListView(APIView):
    def get(self, request):
        users = UserInfo.objects.filter(deleted=False).order_by('-create_time')
        return paginate(request, users, UserInfoSerializer)

    def post(self, request):
        ser = UserCreateSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return success(UserInfoSerializer(ser.instance).data, '创建成功')
        return error(str(ser.errors))


class UserDetailView(BaseDetailView):
    model = UserInfo
    not_found_msg = '用户不存在'

    def get(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error(self.not_found_msg, 404)
        return success(UserInfoSerializer(obj).data)

    def put(self, request, pk):
        obj = self._get_obj(pk)
        if not obj:
            return error(self.not_found_msg, 404)
        ser = UserCreateSerializer(obj, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return success(UserInfoSerializer(ser.instance).data, '更新成功')
        return error(str(ser.errors))
