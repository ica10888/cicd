from django.db import models


class BaseModel(models.Model):
    """公共字段基类"""
    deleted = models.BooleanField(default=False, verbose_name='是否删除')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class AppInfo(BaseModel):
    """应用信息表"""
    STATUS_CHOICES = [
        ('running', '运行中'),
        ('stopped', '已停止'),
        ('deploying', '部署中'),
        ('error', '异常'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='应用名称')
    description = models.TextField(blank=True, verbose_name='应用描述')
    version = models.CharField(max_length=50, default='1.0.0', verbose_name='版本号')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stopped', verbose_name='状态')
    repo_url = models.CharField(max_length=255, blank=True, verbose_name='仓库地址')

    class Meta:
        db_table = 'app_info'
        verbose_name = '应用'
        verbose_name_plural = '应用列表'

    def __str__(self):
        return self.name


class UserInfo(BaseModel):
    """用户信息表"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('user', '普通用户'),
    ]

    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=255, verbose_name='密码')
    email = models.EmailField(blank=True, verbose_name='邮箱')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name='角色')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')

    class Meta:
        db_table = 'user_info'
        verbose_name = '用户'
        verbose_name_plural = '用户列表'

    def __str__(self):
        return self.username


class RoleInfo(BaseModel):
    """权限角色表"""
    ROLE_TYPE_CHOICES = [
        ('developer', '开发人员'),
        ('tester', '测试人员'),
        ('ops', '运维人员'),
    ]

    name = models.CharField(max_length=50, unique=True, verbose_name='角色名称')
    role_type = models.CharField(max_length=20, choices=ROLE_TYPE_CHOICES, verbose_name='角色类型')
    description = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        db_table = 'role_info'
        verbose_name = '角色'
        verbose_name_plural = '角色列表'

    def __str__(self):
        return self.name


class AppPermission(BaseModel):
    """应用权限配置表"""
    role = models.ForeignKey(RoleInfo, on_delete=models.CASCADE, verbose_name='角色')
    app = models.ForeignKey(AppInfo, on_delete=models.CASCADE, null=True, blank=True,
                            verbose_name='应用（为空表示所有应用）')
    can_create = models.BooleanField(default=False, verbose_name='新增权限')
    can_read = models.BooleanField(default=True, verbose_name='查询权限')
    can_update = models.BooleanField(default=False, verbose_name='修改权限')
    can_delete = models.BooleanField(default=False, verbose_name='删除权限')

    class Meta:
        db_table = 'app_permission'
        verbose_name = '应用权限'
        verbose_name_plural = '应用权限列表'
        unique_together = ('role', 'app')

    def __str__(self):
        app_name = self.app.name if self.app else '所有应用'
        return f'{self.role.name} - {app_name}'
