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
router.register(r'players', sfpr.PlayerViewSet, basename='player')
router.register(r'records', sfpr.RecordViewSet, basename='record')


@api_view(['GET'])
def api_root(request):
    return Response({
        'status': 'ok',
        'version': 'v1',
        'endpoints': {
            'users': '/api/v1/users/',
            'auth': '/api/v1/auth/token/',
            'players': '/api/v1/players/',
            'players_search': '/api/v1/players/search/',
            'records': '/api/v1/records/',
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('auth/token/', users.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 