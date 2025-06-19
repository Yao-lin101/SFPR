from django.db.models import Q
import logging
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.sfpr.models import Partner
from apps.sfpr.serializers import (
    PartnerCreateSerializer, 
    PartnerListSerializer, 
    PartnerDetailSerializer
)
from apps.sfpr.permissions import IsAuthenticatedForCreate

# 获取logger
logger = logging.getLogger(__name__)


class PartnerViewSet(viewsets.ModelViewSet):
    """神人记录视图集"""
    queryset = Partner.objects.all()  # 显示所有记录
    permission_classes = [IsAuthenticatedForCreate]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['server']
    search_fields = ['nickname', 'game_id']
    ordering_fields = ['created_at', 'views_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PartnerCreateSerializer
        elif self.action == 'retrieve':
            return PartnerDetailSerializer
        return PartnerListSerializer
    
    def create(self, request, *args, **kwargs):
        """创建神人记录，添加详细日志"""
        logger.info(f"接收到创建神人记录请求，数据: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"数据验证失败: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            self.perform_create(serializer)
            logger.info(f"神人记录创建成功: {serializer.data}")
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.exception(f"创建神人记录时发生异常: {str(e)}")
            return Response({"detail": f"创建失败: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # 增加查看次数
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        搜索神人记录
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
            serializer = PartnerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PartnerListSerializer(queryset, many=True)
        return Response(serializer.data) 