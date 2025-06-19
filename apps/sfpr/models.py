import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


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
    server = models.IntegerField(_("服务器ID"))
    server_name = models.CharField(_("服务器名称"), max_length=50, blank=True)
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
        default='approved'
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
        return f"{self.nickname} ({self.game_id}) - {self.server_name or self.server}"
    
    def increment_views(self):
        """增加查看次数"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def save(self, *args, **kwargs):
        """保存时自动设置服务器名称"""
        # 根据服务器ID获取服务器名称
        SERVER_NAMES = {
            1: "艾欧尼亚", 2: "祖安", 3: "诺克萨斯", 4: "班德尔城", 5: "皮尔特沃夫",
            6: "战争学院", 7: "巨神峰", 8: "雷瑟守备", 9: "裁决之地", 10: "黑色玫瑰",
            11: "暗影岛", 12: "钢铁烈阳", 13: "水晶之痕", 14: "均衡教派", 15: "影流",
            16: "守望之海", 17: "征服之海", 18: "卡拉曼达", 19: "皮城警备", 20: "比尔吉沃特",
            21: "德玛西亚", 22: "弗雷尔卓德", 23: "无畏先锋", 24: "恕瑞玛", 25: "扭曲丛林",
            26: "巨龙之巢", 27: "教育网专区", 28: "男爵领域", 29: "峡谷之巅", 30: "体验服"
        }
        if not self.server_name and self.server:
            self.server_name = SERVER_NAMES.get(self.server, f"未知服务器({self.server})")
        super().save(*args, **kwargs)
