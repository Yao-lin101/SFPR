from rest_framework import serializers
import logging
from .models import Partner

# 获取logger
logger = logging.getLogger(__name__)


class PartnerCreateSerializer(serializers.ModelSerializer):
    """用于创建神人记录的序列化器"""
    
    class Meta:
        model = Partner
        fields = ['nickname', 'game_id', 'server', 'description', 'evidence']
    
    def validate(self, attrs):
        """添加详细的验证逻辑和日志"""
        logger.debug(f"验证创建神人记录数据: {attrs}")
        
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
        
        # 验证神人事迹
        if not attrs.get('description'):
            logger.error("神人事迹为空")
            raise serializers.ValidationError({"description": "神人事迹不能为空"})
        
        return attrs
    
    def create(self, validated_data):
        # 获取当前用户作为提交者
        user = self.context['request'].user
        validated_data['submitter'] = user
        logger.info(f"创建神人记录，提交者: {user.username}, 数据: {validated_data}")
        return super().create(validated_data)


class PartnerListSerializer(serializers.ModelSerializer):
    """用于列表展示的神人记录序列化器"""
    
    class Meta:
        model = Partner
        fields = ['id', 'nickname', 'game_id', 'server_name', 'created_at', 'views_count']


class PartnerDetailSerializer(serializers.ModelSerializer):
    """用于详情展示的神人记录序列化器"""
    submitter_username = serializers.CharField(source='submitter.username', read_only=True)
    
    class Meta:
        model = Partner
        fields = [
            'id', 'nickname', 'game_id', 'server_name', 'description', 
            'evidence', 'submitter_username', 'created_at', 'updated_at', 
            'views_count'
        ] 