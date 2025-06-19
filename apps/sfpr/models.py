import uuid
import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def record_image_path(instance, filename):
    """生成神人事迹图片的存储路径"""
    # 获取文件扩展名
    ext = filename.split('.')[-1].lower()
    
    # 验证扩展名，只允许常见图片格式
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    if ext not in allowed_extensions:
        ext = 'jpg'  # 默认使用jpg扩展名
    
    # 使用时间戳和UUID组合作为文件名，避免文件名冲突
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{timestamp}_{uuid.uuid4().hex[:10]}.{ext}"
    
    # 确保实例和玩家都存在
    if not instance.pk:
        # 如果记录还没有ID，使用临时目录
        return f'records/temp/{new_filename}'
    
    # 获取玩家ID，确保安全
    try:
        player_id = str(instance.player.id) if instance.player and instance.player.id else 'unknown'
    except Exception:
        player_id = 'unknown'
    
    # 使用记录ID和玩家ID组织目录结构
    record_id = str(instance.id) if instance.id else uuid.uuid4().hex
    return f'records/{player_id}/{record_id}/{new_filename}'


class Player(models.Model):
    """玩家模型 - 存储唯一的玩家信息"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nickname = models.CharField(_("昵称"), max_length=100, db_index=True)
    game_id = models.CharField(_("游戏ID"), max_length=50, db_index=True)
    server = models.IntegerField(_("服务器ID"))
    server_name = models.CharField(_("服务器名称"), max_length=50, blank=True)
    
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)
    views_count = models.PositiveIntegerField(_("查看次数"), default=0)
    
    class Meta:
        verbose_name = _("玩家")
        verbose_name_plural = _("玩家")
        ordering = ["-created_at"]
        # 添加唯一性约束
        unique_together = ['nickname', 'game_id', 'server']
        indexes = [
            models.Index(fields=['nickname', 'game_id']),
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


class Record(models.Model):
    """神人事迹记录模型 - 存储对玩家的评价记录"""
    STATUS_CHOICES = (
        ('pending', _('待审核')),
        ('approved', _('已发布')),
        ('rejected', _('已拒绝')),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name=_("玩家")
    )
    description = models.TextField(_("神人事迹"))
    evidence = models.TextField(_("证据"), blank=True, help_text=_("可以是图片链接或描述"))
    
    # 添加图片字段
    image_1 = models.ImageField(_("图片1"), upload_to=record_image_path, blank=True, null=True)
    image_2 = models.ImageField(_("图片2"), upload_to=record_image_path, blank=True, null=True)
    image_3 = models.ImageField(_("图片3"), upload_to=record_image_path, blank=True, null=True)
    
    submitter = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name="submitted_records",
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
    
    class Meta:
        verbose_name = _("神人事迹")
        verbose_name_plural = _("神人事迹")
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.player} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def delete(self, *args, **kwargs):
        """删除记录时同时删除关联的图片文件"""
        # 删除图片文件
        if self.image_1:
            if os.path.isfile(self.image_1.path):
                os.remove(self.image_1.path)
        if self.image_2:
            if os.path.isfile(self.image_2.path):
                os.remove(self.image_2.path)
        if self.image_3:
            if os.path.isfile(self.image_3.path):
                os.remove(self.image_3.path)
        
        # 调用父类的delete方法
        super().delete(*args, **kwargs)
