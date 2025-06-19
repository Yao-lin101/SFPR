from rest_framework import serializers
from .models import Server, Partner


class ServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ['id', 'name', 'region']


class PartnerCreateSerializer(serializers.ModelSerializer):
    """用于创建神人记录的序列化器"""
    
    class Meta:
        model = Partner
        fields = ['nickname', 'game_id', 'server', 'description', 'evidence']
    
    def create(self, validated_data):
        # 获取当前用户作为提交者
        user = self.context['request'].user
        validated_data['submitter'] = user
        return super().create(validated_data)


class PartnerListSerializer(serializers.ModelSerializer):
    """用于列表展示的神人记录序列化器"""
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = Partner
        fields = ['id', 'nickname', 'game_id', 'server_name', 'created_at', 'views_count']


class PartnerDetailSerializer(serializers.ModelSerializer):
    """用于详情展示的神人记录序列化器"""
    server_name = serializers.CharField(source='server.name', read_only=True)
    submitter_username = serializers.CharField(source='submitter.username', read_only=True)
    
    class Meta:
        model = Partner
        fields = [
            'id', 'nickname', 'game_id', 'server_name', 'description', 
            'evidence', 'submitter_username', 'created_at', 'updated_at', 
            'views_count'
        ] 