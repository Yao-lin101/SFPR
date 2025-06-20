from django.db.models import Q, Count
import logging
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.sfpr.models import Player, Record
from apps.sfpr.serializers import (
    PlayerCreateSerializer, 
    PlayerListSerializer, 
    PlayerDetailSerializer,
    RecordSerializer
)
from apps.sfpr.permissions import IsAuthenticatedForCreate, IsRecordOwnerOrReadOnly

# 获取logger
logger = logging.getLogger(__name__)


class PlayerViewSet(viewsets.ModelViewSet):
    """玩家视图集"""
    queryset = Player.objects.all().annotate(records_count=Count('records'))
    permission_classes = [IsAuthenticatedForCreate]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['server']
    search_fields = ['nickname', 'game_id']
    ordering_fields = ['created_at', 'views_count', 'records_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PlayerCreateSerializer
        elif self.action == 'retrieve':
            return PlayerDetailSerializer
        return PlayerListSerializer
    
    def create(self, request, *args, **kwargs):
        """创建玩家"""
        logger.info(f"接收到创建玩家请求，数据: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"数据验证失败: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            player = serializer.save()
            logger.info(f"玩家创建成功，玩家ID: {player.id}")
            headers = self.get_success_headers(serializer.data)
            return Response(PlayerDetailSerializer(player).data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.exception(f"创建玩家时发生异常: {str(e)}")
            return Response({"detail": f"创建失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 增加查看次数
        instance.increment_views()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        搜索玩家
        必填参数: nickname
        选填参数: game_id, server
        """
        nickname = request.query_params.get('nickname')
        game_id = request.query_params.get('game_id', '')
        server_id = request.query_params.get('server', '')
        
        if not nickname:
            return Response(
                {"error": "昵称参数必填"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(nickname__icontains=nickname)
        
        if game_id:
            queryset = queryset.filter(game_id__icontains=game_id)
        
        if server_id:
            queryset = queryset.filter(server=server_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PlayerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PlayerListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_record(self, request, pk=None):
        """
        添加神人事迹记录
        """
        player = self.get_object()
        
        # 验证请求数据
        if not request.data.get('description'):
            return Response(
                {"error": "神人事迹不能为空"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 创建新记录，但先不处理图片
            record = Record.objects.create(
                player=player,
                description=request.data.get('description'),
                evidence=request.data.get('evidence', ''),
                submitter=request.user
            )
            
            # 确保记录已保存并有ID后，再处理图片
            if record.pk:
                # 处理图片上传
                has_images = False
                image_1 = request.FILES.get('image_1')
                image_2 = request.FILES.get('image_2')
                image_3 = request.FILES.get('image_3')
                
                if image_1:
                    record.image_1 = image_1
                    has_images = True
                if image_2:
                    record.image_2 = image_2
                    has_images = True
                if image_3:
                    record.image_3 = image_3
                    has_images = True
                
                # 如果有图片，保存记录
                if has_images:
                    record.save()
                    logger.info(f"为记录 {record.id} 保存了图片")
            
            logger.info(f"为玩家 {player.id} 添加神人事迹记录成功，记录ID: {record.id}")
            return Response(RecordSerializer(record, context={'request': request}).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"添加神人事迹记录时发生异常: {str(e)}")
            return Response({"detail": f"添加失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecordViewSet(viewsets.ModelViewSet):
    """神人事迹记录视图集"""
    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    permission_classes = [IsAuthenticatedForCreate, IsRecordOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['player', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_context(self):
        """
        添加request到序列化器上下文，用于生成完整的媒体URL
        """
        context = super().get_serializer_context()
        return context
    
    @action(detail=False, methods=['get'], url_path='my-records')
    def my_records(self, request):
        """获取当前用户的投稿记录"""
        logger.info(f"接收到获取投稿记录请求，用户: {request.user}")
        
        if not request.user.is_authenticated:
            logger.warning(f"未登录用户尝试访问投稿记录")
            return Response(
                {"error": "未登录用户无法查看投稿记录"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 获取用户的所有投稿记录
        queryset = self.get_queryset().filter(submitter=request.user)
        logger.info(f"用户 {request.user} 的投稿记录数量: {queryset.count()}")
        
        # 包含玩家信息
        queryset = queryset.select_related('player')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) 