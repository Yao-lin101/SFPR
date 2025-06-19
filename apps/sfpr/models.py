import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Server(models.Model):
    """游戏服务器模型"""
    name = models.CharField(_("服务器名称"), max_length=50, unique=True)
    region = models.CharField(_("服务器区域"), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("服务器")
        verbose_name_plural = _("服务器")
        ordering = ["name"]
    
    def __str__(self):
        return self.name


class Partner(models.Model):
    """神人记录模型"""
    STATUS_CHOICES = (
        ('pending', _('待审核')),
        ('approved', _('已发布')),
        ('rejected', _('已拒绝')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(_("昵称"), max_length=100, db_index=True)
    game_id = models.CharField(_("游戏ID"), max_length=50, db_index=True)
    server = models.ForeignKey(
        Server, 
        on_delete=models.CASCADE, 
        related_name="partners",
        verbose_name=_("服务器")
    )
    description = models.TextField(_("神人事迹"))
    evidence = models.TextField(_("证据"), blank=True, help_text=_("可以是图片链接或描述"))
    
    submitter = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="submitted_partners",
        verbose_name=_("提交者")
    )
    
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    
    status = models.CharField(
        _("状态"), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    views_count = models.PositiveIntegerField(_("查看次数"), default=0)
    
    class Meta:
        verbose_name = _("神人记录")
        verbose_name_plural = _("神人记录")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['nickname', 'game_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.nickname} ({self.game_id}) - {self.server}"
    
    def increment_views(self):
        """增加查看次数"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
