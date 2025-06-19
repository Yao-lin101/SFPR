from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from .views import users, sfpr

# 创建路由器
router = DefaultRouter()

# 注册视图集
router.register(r'users', users.UserViewSet, basename='user')
router.register(r'servers', sfpr.ServerViewSet, basename='server')
router.register(r'partners', sfpr.PartnerViewSet, basename='partner')


@api_view(['GET'])
def api_root(request):
    return Response({
        'status': 'ok',
        'version': 'v1',
        'endpoints': {
            'users': '/api/v1/users/',
            'auth': '/api/v1/auth/token/',
            'servers': '/api/v1/servers/',
            'partners': '/api/v1/partners/',
            'partners_search': '/api/v1/partners/search/',
        }
    })

urlpatterns = [
    # API 根路径
    path('', api_root, name='api-root'),
    
    # JWT 认证
    path('auth/token/', users.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 需要认证的路由放在后面
    path('', include(router.urls)),
    # 遗嘱配置路由
] 