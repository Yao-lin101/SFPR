from rest_framework import serializers
import logging
import os
# import magic  # 暂时注释掉
from .models import Player, Record
from django.conf import settings
from django.core.exceptions import ValidationError

# 获取logger
logger = logging.getLogger(__name__)


def validate_image_file(file):
    """验证上传的文件是否为有效的图片"""
    if not file:
        return file
    
    # 检查文件大小
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("图片大小不能超过5MB")
    
    # 检查文件扩展名
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if ext not in valid_extensions:
        raise ValidationError(f"不支持的图片格式。支持的格式有: {', '.join(valid_extensions)}")
    
    # 暂时注释掉python-magic检查
    # try:
    #     file_content = file.read()
    #     file.seek(0)  # 重置文件指针
    #     mime = magic.from_buffer(file_content, mime=True)
    #     
    #     valid_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    #     if mime not in valid_mimes:
    #         raise ValidationError(f"文件类型错误。检测到的MIME类型: {mime}")
    # except Exception as e:
    #     logger.error(f"图片验证错误: {str(e)}")
    #     raise ValidationError("无法验证图片格式，请确保上传的是有效图片文件")
    
    # 简单检查文件内容的前几个字节
    try:
        # 读取文件头部
        file.seek(0)
        header = file.read(8)
        file.seek(0)
        
        # 检查是否为常见图片格式的文件头
        # JPEG: FF D8
        # PNG: 89 50 4E 47
        # GIF: 47 49 46 38
        if not (
            (header[0:2] == b'\xFF\xD8') or  # JPEG
            (header[0:4] == b'\x89PNG') or   # PNG
            (header[0:4] == b'GIF8')         # GIF
        ):
            logger.warning(f"文件 {file.name} 的文件头不匹配常见图片格式")
            # 但我们不抛出异常，让Django的ImageField自己验证
    except Exception as e:
        logger.error(f"检查图片文件头时出错: {str(e)}")
        # 同样，我们不抛出异常
    
    return file


class RecordSerializer(serializers.ModelSerializer):
    """神人事迹记录序列化器"""
    submitter_username = serializers.CharField(source='submitter.username', read_only=True)
    player = serializers.SerializerMethodField()
    image_1_url = serializers.SerializerMethodField()
    image_2_url = serializers.SerializerMethodField()
    image_3_url = serializers.SerializerMethodField()
    image_1 = serializers.ImageField(write_only=True, required=False, validators=[validate_image_file])
    image_2 = serializers.ImageField(write_only=True, required=False, validators=[validate_image_file])
    image_3 = serializers.ImageField(write_only=True, required=False, validators=[validate_image_file])
    
    class Meta:
        model = Record
        fields = [
            'id', 'description', 'evidence', 'submitter_username', 
            'created_at', 'status', 'player', 
            'image_1', 'image_2', 'image_3',
            'image_1_url', 'image_2_url', 'image_3_url'
        ]
        read_only_fields = ['submitter_username', 'created_at', 'status']
        extra_kwargs = {
            'image_1': {'write_only': True},
            'image_2': {'write_only': True},
            'image_3': {'write_only': True},
        }
    
    def get_player(self, obj):
        """返回玩家信息"""
        return {
            'id': str(obj.player.id),
            'nickname': obj.player.nickname,
            'game_id': obj.player.game_id,
            'server': obj.player.server,
            'server_name': obj.player.server_name,
        }
    
    def get_image_1_url(self, obj):
        if obj.image_1:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_1.url)
            return obj.image_1.url
        return None
    
    def get_image_2_url(self, obj):
        if obj.image_2:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_2.url)
            return obj.image_2.url
        return None
    
    def get_image_3_url(self, obj):
        if obj.image_3:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_3.url)
            return obj.image_3.url
        return None


class PlayerListSerializer(serializers.ModelSerializer):
    """用于列表展示的玩家序列化器"""
    records_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = ['id', 'nickname', 'game_id', 'server_name', 'created_at', 'views_count', 'records_count']
    
    def get_records_count(self, obj):
        return obj.records.filter(status='approved').count()


class PlayerDetailSerializer(serializers.ModelSerializer):
    """用于详情展示的玩家序列化器"""
    records = RecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Player
        fields = [
            'id', 'nickname', 'game_id', 'server', 'server_name',
            'created_at', 'updated_at', 'views_count', 'records'
        ]


class PlayerCreateSerializer(serializers.ModelSerializer):
    """用于创建玩家的序列化器"""
    class Meta:
        model = Player
        fields = ['nickname', 'game_id', 'server']
    
    def validate(self, attrs):
        """添加详细的验证逻辑和日志"""
        logger.debug(f"验证创建玩家数据: {attrs}")
        
        # 验证昵称
        if not attrs.get('nickname'):
            logger.error("昵称为空")
            raise serializers.ValidationError({"nickname": "昵称不能为空"})
        
        # 验证游戏ID
        if not attrs.get('game_id'):
            logger.error("游戏ID为空")
            raise serializers.ValidationError({"game_id": "游戏ID不能为空"})
        
        # 验证服务器
        server_id = attrs.get('server')
        if not server_id:
            logger.error("服务器为空")
            raise serializers.ValidationError({"server": "服务器不能为空"})
        
        # 验证服务器ID是否有效
        valid_server_ids = list(range(1, 31))  # 1-30
        if server_id not in valid_server_ids:
            logger.error(f"无效的服务器ID: {server_id}")
            raise serializers.ValidationError({"server": f"无效的服务器ID: {server_id}"})
        
        return attrs 