from rest_framework import serializers
import logging
from .models import Player, Record

# 获取logger
logger = logging.getLogger(__name__)


class RecordSerializer(serializers.ModelSerializer):
    """神人事迹记录序列化器"""
    submitter_username = serializers.CharField(source='submitter.username', read_only=True)
    player = serializers.SerializerMethodField()
    
    class Meta:
        model = Record
        fields = ['id', 'description', 'evidence', 'submitter_username', 'created_at', 'status', 'player']
        read_only_fields = ['submitter_username', 'created_at', 'status']
    
    def get_player(self, obj):
        """返回玩家信息"""
        return {
            'id': str(obj.player.id),
            'nickname': obj.player.nickname,
            'game_id': obj.player.game_id,
            'server': obj.player.server,
            'server_name': obj.player.server_name,
        }


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
    description = serializers.CharField(write_only=True, required=True)
    evidence = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Player
        fields = ['nickname', 'game_id', 'server', 'description', 'evidence']
    
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
        
        # 验证神人事迹
        if not attrs.get('description'):
            logger.error("神人事迹为空")
            raise serializers.ValidationError({"description": "神人事迹不能为空"})
        
        return attrs
    
    def create(self, validated_data):
        """创建玩家和神人事迹记录"""
        # 提取神人事迹相关字段
        description = validated_data.pop('description')
        evidence = validated_data.pop('evidence', '')
        
        # 获取当前用户
        user = self.context['request'].user
        
        # 检查玩家是否已存在
        try:
            player = Player.objects.get(
                nickname=validated_data['nickname'],
                game_id=validated_data['game_id'],
                server=validated_data['server']
            )
            logger.info(f"玩家已存在，ID: {player.id}")
        except Player.DoesNotExist:
            # 创建新玩家
            player = Player.objects.create(**validated_data)
            logger.info(f"创建新玩家，ID: {player.id}")
        
        # 创建神人事迹记录
        record = Record.objects.create(
            player=player,
            description=description,
            evidence=evidence,
            submitter=user
        )
        logger.info(f"创建神人事迹记录，ID: {record.id}")
        
        return player 