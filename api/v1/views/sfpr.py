from django.db.models import Q
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.sfpr.models import Server, Partner
from apps.sfpr.serializers import (
    ServerSerializer, 
    PartnerCreateSerializer, 
    PartnerListSerializer, 
    PartnerDetailSerializer
)
from apps.sfpr.permissions import IsAuthenticatedForCreate


class ServerViewSet(viewsets.ReadOnlyModelViewSet):
    """服务器视图集，只读"""
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    permission_classes = [permissions.AllowAny]


class PartnerViewSet(viewsets.ModelViewSet):
    """神人记录视图集"""
    queryset = Partner.objects.filter(status='approved')
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
            queryset = queryset.filter(server_id=server_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = PartnerListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PartnerListSerializer(queryset, many=True)
        return Response(serializer.data) 